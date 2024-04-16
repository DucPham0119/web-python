function generateQuiz() {
    var numQuestions = document.getElementById('numQuestions').value;
    var quizContainer = document.getElementById('quizContainer');
    quizContainer.innerHTML = ''; // Xóa nội dung cũ (nếu có)

    for (var i = 0; i < numQuestions; i++) {
        var questionNumber = i + 1;

        var questionContainer = document.createElement('div');
        questionContainer.classList.add('question-container');

        var questionLabel = document.createElement('label');
        questionLabel.textContent = 'Đáp án câu ' + questionNumber + ':';
        questionLabel.classList.add('question-label');

        var answerInput = document.createElement('input');
        answerInput.setAttribute('type', 'text');
        answerInput.setAttribute('name', 'answer' + questionNumber);
        answerInput.classList.add('answer-input');
        answerInput.setAttribute('autocomplete', 'off');

        questionContainer.appendChild(questionLabel);
        questionContainer.appendChild(answerInput);
        quizContainer.appendChild(questionContainer);
    }

    // Hiển thị nút "Submit" sau khi đã tạo câu trắc nghiệm
    var submitButton = document.getElementById('submitButton');
    submitButton.style.display = 'block';
}

document.getElementById('quizForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Ngăn chặn việc submit mặc định của form

    var numQuestions = document.getElementById('numQuestions').value;
    var answers = {}; // Đối tượng JSON chứa các đáp án

    for (var i = 0; i < numQuestions; i++) {
        var questionNumber = i + 1;
        var answerInput = document.querySelector('input[name="answer' + questionNumber + '"]');
        answers['answer' + questionNumber] = answerInput.value;
    }

    // Chuyển đổi đối tượng JSON thành chuỗi JSON
    var jsonAnswers = JSON.stringify(answers);

    // Ghi dữ liệu lên server
    return fetch("http://127.0.0.1:5000/savejson", {
        headers: {
            version: 1,
            "content-type": "application/json"
        },
        method: "POST",
        body: jsonAnswers
    })
        .then(res => {
            if (!res.ok) {
                throw res.statusText;
            }
            window.location.href = 'http://127.0.0.1:5500/client/index.html';
            alert('Lưu đáp án thành công');
            
            // return res.text();
        })
        .catch(err => alert("Error:", err));
});

