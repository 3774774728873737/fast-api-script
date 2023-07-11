function handleFileUpload(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);
  
  fileInput.onchange = function () {
    var files = fileInput.files;

    var videoPlayer = document.getElementById('videoPlayer' + videoNumber);
    var videoThumbnail = document.getElementById('videoThumbnail' + videoNumber);

    videoPlayer.style.display = 'none';
    videoThumbnail.style.display = 'block';
    videoThumbnail.style.width = '100%'; // Set the width to 450 pixels
    videoThumbnail.style.height = '100%'; // Set the height to 540 pixels
    
    // Set placeholder image
    videoThumbnail.src = 'load.png';

    var formData = new FormData();
    for (var i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    formData.append('videoNumber', videoNumber); // Add the videoNumber to the formData

    fetch('https://fast-api-script-0d0703f4a5dc.herokuapp.com/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.message); // Display the message

        if (data.imagePath) {
          // Add a cache-busting parameter to the image URL
          var imageURL = data.imagePath + '?' + new Date().getTime();
          videoThumbnail.src = imageURL; // Replace placeholder with actual image
        } else {
          videoThumbnail.src = 'load.png'; // Keep placeholder if no thumbnail available
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  fileInput.click();
}


// Function to handle file upload for video 2 and video 3
function chooseFile(videoNumber) {
  var fileInput = document.getElementById('fileInput' + videoNumber);
  fileInput.onchange = function () {
    handleFileUpload(videoNumber);
  };
  fileInput.click();
}

// Add event listeners to the file input elements when the page is loaded
document.addEventListener("DOMContentLoaded", function() {
  var fileInputs = document.querySelectorAll("input[type='file']");
  fileInputs.forEach(function(fileInput) {
    fileInput.addEventListener('change', function() {
      var videoNumber = this.id.replace("fileInput", "");
      handleFileUpload(videoNumber);
    });
  });
});
