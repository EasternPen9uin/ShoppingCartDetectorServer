import { BACKEND_URL, requireNormalUser, getCSRF } from "./common/common_module.js";


// 캔버스에 카메라 그릴 간격 (카메라 프레임 간격, 밀리초 단위)
const CAMERA_FPS = 40;
// 백엔드에서 요청 되돌아오고 <-> 다시 백엔드로 요청 보내는 사이의 간격
const REQUEST_WAIT = 700;

// canvas에 카메라 프레임을 그리기 위해 사용
const video = document.getElementById("videoElement"); 
// 박스 그릴 canvas와 context
const canvas = document.querySelector("#main_canvas"); 
let ctx = canvas.getContext("2d");
// 박스가 그려지지 않은 사진을 백엔드로 보내기 위해 사용하는 canvas와 그 context 
const hidden_canvas = document.querySelector("#hidden_canvas"); 
let hidden_ctx = hidden_canvas.getContext("2d");
// 카메라 선택창
const select = document.querySelector("#camlist");
// 알람
const alarm  = document.querySelector("#hidden_alarm");
// 경계 박스 저장용
let borderboxes_list = []; 
// 사용 가능한 카메라들의 인덱스와 id값을 저장하기 위한 객체
let videoinput_table = {};
// 백엔드 서버 연결 끊겼는지 확인할 용도. 
// 연결 끊기면(5회 연속 연결 실패시) setTimeout 재귀실행 중단
let err_count = 0; 


pageMain();
async function pageMain() {
    // 노말유저 권한 요구
    await requireNormalUser();
    // 사용 가능한 카메라 리스트를 모두 구함
    const videoinput_list = (await navigator.mediaDevices.enumerateDevices())
                            .filter(d => d.kind=="videoinput");
    // 없으면 에러
    if(videoinput_list.length == 0) {
        alert("현재 사용가능한 카메라가 없습니다!");
        return;
    }
    // 사용 가능한 카메라들을 카메라 변경하는 버튼에 하나씩 추가
    for(let i=0; i < videoinput_list.length; i++) {
        let option = document.createElement("option");
        videoinput_table[i] = [videoinput_list[i].deviceId]
        option.innerText = `[${i}] ` + videoinput_list[i].label;
        select.append(option);
    }
    // 처음 카메라와 비디오 연결 및 캔버스 크기 조정
    await selectCamera();
    // (주)캔버스 누르면 전체화면 되게 만들기
    canvas.addEventListener("click", function() {canvas.requestFullscreen();});
    // 카메라 변경 기능 추가
    select.onchange = selectCamera;
    // CAMERA_FPS 만큼의 밀리초마다 캔버스에 카메라 그리기
    setInterval(doItOncePerFPS, CAMERA_FPS);
    // REQUEST_WAIT 후에 사진 추론 보내는 사이클 시작
    setTimeout(inferImage, REQUEST_WAIT);
}

// select에 선택된 카메라로 변경
async function selectCamera() {
    let idx = findNumInOneOptionString(select.value);
    let stream = null;

    stream = await navigator.mediaDevices.getUserMedia({
        video: {
            deviceId : videoinput_table[idx],
            width : {ideal : 640},
            height : {ideal : 360}
        }
    });

    video.srcObject = stream;
    while(video.videoWidth==0 && video.videoHeight==0) {
        await sleep(40);
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    hidden_canvas.width = video.videoWidth;
    hidden_canvas.height = video.videoHeight;
    // 300px : ?px = video.videoWidth : video.videoHeight
    // ? = (video.videoHeight*300 / video.videoWidth) + px!
    canvas.style.height = (video.videoHeight*300 / video.videoWidth) + "px";
    //alert("해상도 : (" + video.videoWidth + ", " + video.videoHeight + ")");
}

function doItOncePerFPS() {
    drawCameraInCanvas(); // 캔버스에 카메라 그리기
    if(borderboxes_list.length >= 1) {
        // 알람 꺼져있으면 울리게
        if(alarm.paused) {
            alarm.play(); // 경보 울리기
        }
        for(let i=0; i < borderboxes_list.length; i++) {
            drawBoxInCanvas(...borderboxes_list[i]); // 검출결과를 박스로 그리기
        }
    }
}

// (주)캔버스에 카메라 그리기
function drawCameraInCanvas() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
}

// 숨겨진 캔버스에 카메라 그리기
function drawCameraInHiddenCanvas() {
    hidden_ctx.drawImage(video, 0, 0, hidden_canvas.width, hidden_canvas.height);
}

// 숨겨진 캔버스에 카메라를 그린 후, 
// 해당 캔버스에서 사진을 찍어 jpeg형식의 blob으로 바꾸어 반환
async function getBlobFromWebcam() {
    drawCameraInHiddenCanvas();
    const blob = await new Promise(resolve => hidden_canvas.toBlob(resolve, 'image/jpeg', 0.95));
    return blob;
}

// 찍은 사진을 백엔드에 보내서 추론을 요청함
// 요청을 받았다면 쇼핑카트의 좌표랑 기타등등을 borderboxes_list에 넣음
// (박스 그리는건 이 함수가 안 하고, fps마다 실행되는 다른 함수가 함)
// 1대 이상 검출되었다면 alarm 켬
// 끝나면 다시 setTimeOut같은거 써서 재귀적으로 실행되게 함
async function inferImage() {
    console.time(); // 시간측정용
    const blob = await getBlobFromWebcam();
    let file = new File([blob], 'image.jpg', {type:'image/jpeg'});
    let formData = new FormData();
    formData.append("image", file);
    
    try{
        const response = await fetch(BACKEND_URL+"yolo/inferimage", {
            method : "POST",
            headers : {
                'X-CSRFToken' : getCSRF(),
            },
            body : formData
        });
        const responseJson = await response.json();
        if(responseJson.status_code == 200) {
            borderboxes_list = responseJson.bounding_boxes;
        }
        else {
            console.log(responseJson);
        }
    }
    catch(e) {
        console.log(e);
        // 백엔드서버 연결 오류 발생시 
        // 검출된 박스를 다 지워서 알람 안 울리게 하기
        borderboxes_list = []; 
        if((++err_count) >= 5) {
            alert("백엔드 서버와의 연결이 끊겼습니다!");
            return;
        }
    }
    console.timeEnd();
    setTimeout(inferImage, REQUEST_WAIT); // 재귀적으로 자기 자신을 실행
}

// select에서 인덱스 뽑아내기
function findNumInOneOptionString(inputString) {
    const match = inputString.match(/\[\d+\]/);
    const extractedNumber = Number(match[0].match(/\d+/)[0]); // 숫자만 추출하고 숫자로 변환
    return extractedNumber;
}

// sleep용 비동기 promise
function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// (주)캔버스상에 박스 그리기
// (처음x, 처음y, 끝x, 끝y) 순으로 들어온 float(0~1)값 좌표를 가지고 박스그림
function drawBoxInCanvas(x0, y0, x1, y1) {
    // 실수 : strokeRect는 ymin값이 
    ctx.strokeStyle = 'red';
    ctx.lineWidth = canvas.width / 100;
    const val_x0 = x0 * canvas.width;
    const val_y0 = y0 * canvas.height;
    const tmp_val_x1 = (x1-x0)*canvas.width; 
    const val_x1 = tmp_val_x1 < canvas.width-val_x0 ? tmp_val_x1 : canvas.width-val_x0;
    const tmp_val_y1 = (y1-y0)*canvas.height;
    const val_y1 = tmp_val_y1 < canvas.height-val_y0 ? tmp_val_y1 : canvas.height-val_y0;
    ctx.strokeRect(
        val_x0,
        val_y0,
        val_x1,
        val_y1,
    );
}

