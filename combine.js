function combine() {
  var loadedVideos = 0;
  var videosToLoad = 2; // Minimum number of videos required

  // Check if each video is loaded
  for (var i = 1; i <= 3; i++) {
    var videoThumbnail = document.getElementById('videoThumbnail' + i);
    // check if word html in src of videoThumbnail if not include then ++
    if (videoThumbnail.src.includes('html')) {
      // pass it
    } else {
      loadedVideos++;
    }

    console.log(loadedVideos);
  }

  if (loadedVideos >= videosToLoad) {
    var loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');

    fetch('http://localhost:8000/combine')
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
