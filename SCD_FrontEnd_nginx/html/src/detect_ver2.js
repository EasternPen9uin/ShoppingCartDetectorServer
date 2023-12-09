import { drawBoxInCanvas, getWebSocket } from "./common/common_module.js";


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

// 웹소켓 저장용
let socket = undefined;
// 시간 측정용
let time = new Date();


pageMain();
async function pageMain() {
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

    // 웹소켓 연결 시도
    try {
        socket = await getWebSocket("inferImage");
        socket.onmessage = putBoundingBoxes;
        socket.onclose = deleteAllBoundingBoxesAndShowAlert;
        // 소켓 연결 후, REQUEST_WAIT만큼 기다린 후에 사진 추론 보내는 사이클 시작
        socket.onopen = () => {
            setTimeout(inferImage, REQUEST_WAIT);
        }
    }
    catch(e) {
        // 연결 실패시 에러 띄우고 코드 중단.
        alert(e);
        return;
    }
    
    // CAMERA_FPS 만큼의 밀리초마다 캔버스에 카메라 그리기
    setInterval(doItOncePerFPS, CAMERA_FPS);
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
            drawBoxInCanvas(ctx, canvas, ...borderboxes_list[i]); // 검출결과를 박스로 그리기
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
    time = new Date(); // 시간 측정용
    const blob = await getBlobFromWebcam();
    await socket.send(blob);
}

// 서버로부터 연락이 왔을 때, 거기서 바운딩박스 정보를 꺼내서 js내 바운딩박스에 넣음
// 원래 RESTFUL API시절에는 inferImage안에 있었으나,
// 웹소켓으로 바꾸면서 받는 부분을 함수로 따로 뺄 필요가 있었음
function putBoundingBoxes(event) {
    console.log(new Date() - time);
    borderboxes_list = JSON.parse(event.data).bounding_boxes;
    // event.data가 객체로 들어올 줄 알았는데 그냥 JSON문자열 그대로 들어옴...
    setTimeout(inferImage, REQUEST_WAIT); // 바운딩박스 다 넣었다면 다시 inferimage 실행
}

// 연결 끊겼을 때 알람 안울리게 만들고, alert로 알림
function deleteAllBoundingBoxesAndShowAlert() {
    // 에러 발생시 검출된 박스를 다 지워서 알람 안 울리게 하기
    borderboxes_list = []; 
    // 에러 표시 후 리턴(반복구조 중단)
    alert("백엔드 서버와의 연결이 끊겼습니다!");
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

