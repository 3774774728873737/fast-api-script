function combine() {
  var loadedVideos = [];
  var videosToLoad = 2; // Minimum number of videos required

  // Check if each video is loaded
  for (var i = 1; i <= 3; i++) {
    var videoThumbnail = document.getElementById('videoThumbnail' + i);
    // check if the word mp4 is included in the src of videoThumbnail
    if (videoThumbnail.src.includes('.mp4')) {
      loadedVideos.push(videoThumbnail.src);
    }
  }

  console.log(loadedVideos);

  if (loadedVideos.length >= videosToLoad) {
    var loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');

    // Create FormData object to store your files
    var formData = new FormData();

    // Add each video to the FormData object
    loadedVideos.forEach((src, index) => {
      // Fetch the video file from the src URL, then append it to the FormData
      fetch(src)
        .then(response => response.blob())
        .then(blob => {
          formData.append(`file${index + 1}`, blob, `video${index + 1}.mp4`);
        });
    });

    // Send POST request with the FormData object
    fetch('/combine', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (response.ok) {
        return response.blob();
      } else {
        throw new Error('Unable to combine videos');
      }
    })
    .then(blob => {
      var downloadLink = document.createElement('a');
      downloadLink.href = URL.createObjectURL(blob);
      downloadLink.download = 'combined.mp4';

      downloadLink.click();
      loadingOverlay.classList.remove('active'); // Hide the loading overlay
    })
    .catch(error => {
      console.error('Error:', error);
      loadingOverlay.classList.remove('active'); // Hide the loading overlay
    });
  } else {
    console.log('At least 2 videos must be loaded');
  }
}
