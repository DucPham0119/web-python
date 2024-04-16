// STEP 1: select element and register change event
const imagePreview = document.querySelector('[data-target="image-preview"]');
const spinner = document.querySelector('[data-target="spinner"]');
const fileUploader = document.querySelector('[data-target="file-uploader"]');
const submitButton = document.getElementById('submitQuizBtn');
const imagePreviewRight = document.querySelector('[data-target="image-preview-right"]');
const spinnerRight = document.querySelector('[data-target="spinner-right"]');
const studentId = document.getElementById('studentId');
const score = document.getElementById('score');

fileUploader.addEventListener("change", handleFileUpload);
submitButton.addEventListener("click", handleQuizSubmission);

let uploadedImage = null; // Lưu trữ hình ảnh đã tải lên
let response = null;


async function handleFileUpload(e) {
  try {
    const file = e.target.files[0];
    setUploading(true);
    if (!file) return;

    const beforeUploadCheck = await beforeUpload(file);
    if (!beforeUploadCheck.isValid) throw beforeUploadCheck.errorMessages;

    showPreviewImage(file);
    uploadedImage = file
    alert("File Uploaded Success");
  } catch (error) {
    alert("Error Upload: ", error);
  } finally {
    e.target.value = '';  // reset input file
    setUploading(false);
  }
}

// STEP 2: showPreviewImage with createObjectURL
// If you prefer Base64 image, use "FileReader.readAsDataURL"
function showPreviewImage(fileObj) {
  const image = URL.createObjectURL(fileObj);
  imagePreview.src = image;
}

// STEP 3: change file object into ArrayBuffer
function getArrayBuffer(fileObj) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    // Get ArrayBuffer when FileReader on load
    reader.addEventListener("load", () => {
      resolve(reader.result);
    });

    // Get Error when FileReader on error
    reader.addEventListener("error", () => {
      reject("error occurred in getArrayBuffer");
    });

    // read the blob object as ArrayBuffer
    // if you nedd Base64, use reader.readAsDataURL
    reader.readAsDataURL(fileObj);
  });
}

async function handleQuizSubmission() {
  console.log("submit");
  if (!uploadedImage) {
    alert("Vui lòng tải lên hình ảnh trước khi chấm bài!");
    return;
  }

  const arrayBuffer = await getArrayBuffer(uploadedImage);
  const base64Img = arrayBuffer.split("base64,")[1]

  response = uploadFileAJAX(base64Img)
    .then(response => {
      setUploadingRight(true)
      console.log(response)
      alert("Đã chấm bài thành công!");
      console.log(response['anh_dc_cham'])
      uploadByBase64(response['anh_dc_cham'])
      studentId.textContent = 'Student Id: ' + response['student_id'];
      score.textContent = response['score'];
    })
    .catch(error => {
      alert("Lỗi khi chấm bài: " + error);
      setUploadingRight(false);
    });
  
}

// STEP 4: upload file throguth AJAX
// - use "new Uint8Array()"" to change ArrayBuffer into TypedArray
// - TypedArray is not a truely Array,
//   use "Array.from()" to change it into Array
function uploadFileAJAX(arrayBuffer) {
  return fetch("http://127.0.0.1:5000", {
    headers: {
      version: 1,
      "content-type": "application/json"
    },
    method: "POST",
    body: JSON.stringify({
      imageId: 1,
      image: arrayBuffer
    })
  })
    .then(res => {
      if (!res.ok) {
        throw res.statusText;
      }
      return res.json();
    })
    .then(data => data)
    .catch(err => console.log("err", err));
}

// STEP 5: Create before upload checker if needed
function beforeUpload(fileObject) {
  return new Promise(resolve => {
    const validFileTypes = ["image/jpeg", "image/png"];
    const isValidFileType = validFileTypes.includes(fileObject.type);
    let errorMessages = [];

    if (!isValidFileType) {
      errorMessages.push("You can only upload JPG or PNG file!");
    }

    resolve({
      isValid: isValidFileType,
      errorMessages: errorMessages.join("\n")
    });
  });
}

function setUploading(isUploading) {
  if (isUploading === true) {
    spinner.classList.add("opacity-1");
  } else {
    spinner.classList.remove("opacity-1");
  }
}

function setUploadingRight(isUploading) {
  if (isUploading === true) {
    spinnerRight.classList.add("opacity-1");
  } else {
    spinnerRight.classList.remove("opacity-1");
  }
}

function uploadByBase64(base64Img) {
  const imageDataUrl = 'data:image/jpeg;base64,' + base64Img;
  imagePreviewRight.src = imageDataUrl;
}