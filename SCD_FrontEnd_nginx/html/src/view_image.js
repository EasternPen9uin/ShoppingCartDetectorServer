import { drawBoxInCanvas, sendMyRequest } from "./common/common_module.js";

const canvas = document.querySelector("#viewImageCanvas");
const ctx = canvas.getContext("2d");
const hiddenImage = document.querySelector("#hiddenImage");
const dateTime = document.querySelector("#dateTime");
const username = document.querySelector("#username");
const detectedShoppingCarts = document.querySelector("#detectedShoppingCarts");
const prev = document.querySelector("#prev");
const next = document.querySelector("#next");
const picIdText = document.querySelector("#picIdText");
const deleteBtn = document.querySelector("#deleteBtn");

let pictureId = null;
let boundingBoxes = null;
let image_src = null;
let username_text = null;
let date_text = null;
let carts_text = null;

pageMain();
async function pageMain() {
    pictureId = localStorage.getItem("pictureId");
    // ImageSearch사이트에서 넘어온게 아니라면
    if(pictureId===null) {
        alert("올바르지 못한 접근입니다.");
        return;
    }
    await showPic(pictureId);
    prev.onclick = async () => {await prevBtn();};
    next.onclick = async () => {await nextBtn();};
    deleteBtn.onclick = async () => {await deleteImage();};
    localStorage.removeItem("pictureId");
    
}

async function showPic(arg_id) {
    pictureId = arg_id;
    const body = { id : pictureId };
    const responseJson = await sendMyRequest("yolo/getpic", "POST", body);
    if(responseJson.status_code !== 200) {
		// 모종의 이유로 실패
		alert(responseJson.detail);
		return;
	}
    username_text = responseJson.username;
    date_text = responseJson.date;
    image_src = responseJson.nowPath;
    boundingBoxes = responseJson.nowBoundingBox;
    
    drawImageInCanvas();
    changeText();
    undisableAllBtns();
}

async function prevBtn() {
    disableAllBtns();
    const body = { id : pictureId}
    const responseJson = await sendMyRequest("yolo/getprevpic", "POST", body);
    if(responseJson.status_code !== 200) {
		// 모종의 이유로 실패
		alert(responseJson.detail);
        undisableAllBtns();
		return;
	}

    pictureId = responseJson.prevId;
    username_text = responseJson.username;
    date_text = responseJson.date;
    image_src = responseJson.prevPath;
    boundingBoxes = responseJson.prevBoundingBox;
    drawImageInCanvas();
    changeText();
    undisableAllBtns();
}

async function nextBtn() {
    disableAllBtns();
    const body = { id : pictureId}
    const responseJson = await sendMyRequest("yolo/getnextpic", "POST", body);
    if(responseJson.status_code !== 200) {
		// 모종의 이유로 실패
		alert(responseJson.detail);
		undisableAllBtns();
        return;
	}

    pictureId = responseJson.nextId;
    username_text = responseJson.username;
    date_text = responseJson.date;
    image_src = responseJson.nextPath;
    boundingBoxes = responseJson.nextBoundingBox;
    drawImageInCanvas();
    changeText();
    undisableAllBtns();
}

async function deleteImage() {
    // 생성할건지 묻는 창 띄우가
	if(confirm(`사진을 정말로 삭제하시겠습니까?`) == false) {
		return;	
	}
    const body = { id : pictureId};
    const responseJson = await sendMyRequest("yolo/deleteimage", "DELETE", body);
    if(responseJson.status_code !== 200) {
		// 모종의 이유로 실패
		alert(responseJson.detail);
		return;
	}
    alert("사진이 삭제되었습니다!");
    if(responseJson.nextPicId != null) {
        showPic(responseJson.nextPicId);
    }
    else if(responseJson.prevPicId != null) {
        showPic(responseJson.prevPicId);
    }
    else {
        alert("더 이상 남아있는 사진이 없습니다!");
    }
}

function drawImageInCanvas() {
    hiddenImage.onload = function() {
        canvas.width = hiddenImage.naturalWidth;
        canvas.height = hiddenImage.naturalHeight;
        canvas.style.width = parseInt((canvas.height * hiddenImage.naturalWidth) / hiddenImage.naturalHeight)
        ctx.drawImage(hiddenImage, 0, 0, canvas.width, canvas.height);
        for(let i=0; i<boundingBoxes.length; i++) {
            const boundingBox_withoutId = [boundingBoxes[i][1], boundingBoxes[i][2], boundingBoxes[i][3], boundingBoxes[i][4]]
            drawBoxInCanvas(ctx, canvas, ...boundingBox_withoutId);
        }
        console.log(boundingBoxes);
    }
    hiddenImage.src = image_src;
}

function changeText() {
    dateTime.textContent = date_text;
    username.textContent = username_text;
    detectedShoppingCarts.textContent = boundingBoxes.length;
    picIdText.textContent = pictureId;
}

function disableAllBtns() {
    next.disabled = true;
    prev.disabled = true;
}

function undisableAllBtns() {
    next.disabled = false;
    prev.disabled = false;
}