var dates = new Array(); // Lyrics timing
var startSeconds; // Start time
var linesCount; // Number of Lyric lines


navigator.mediaDevices.getUserMedia({audio:true})
.then(stream => {handlerFunction(stream)})


function getAllUrlParams(url) {

  // get query string from url (optional) or window
  var queryString = url ? url.split('?')[1] : window.location.search.slice(1);

  // we'll store the parameters here
  var obj = {};
  // if query string exists
  if (queryString) {

    // stuff after # is not part of query string, so get rid of it
    queryString = queryString.split('#')[0];

    // split our query string into its component parts
    var arr = queryString.split('&');

    for (var i = 0; i < arr.length; i++) {
      // separate the keys and the values
      var a = arr[i].split('=');

      // set parameter name and value (use 'true' if empty)
      var paramName = a[0];
      var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];

      // (optional) keep case consistent
      paramName = paramName.toLowerCase();
      if (typeof paramValue === 'string') paramValue = paramValue.toLowerCase();

      // if the paramName ends with square brackets, e.g. colors[] or colors[2]
      if (paramName.match(/\[(\d+)?\]$/)) {

        // create key if it doesn't exist
        var key = paramName.replace(/\[(\d+)?\]/, '');
        if (!obj[key]) obj[key] = [];

        // if it's an indexed array e.g. colors[2]
        if (paramName.match(/\[\d+\]$/)) {
          // get the index value and add the entry at the appropriate position
          var index = /\[(\d+)\]/.exec(paramName)[1];
          obj[key][index] = paramValue;
        } else {
          // otherwise add the value to the end of the array
          obj[key].push(paramValue);
        }
      } else {
        // we're dealing with a string
        if (!obj[paramName]) {
          // if it doesn't exist, create property
          obj[paramName] = paramValue;
        } else if (obj[paramName] && typeof obj[paramName] === 'string'){
          // if property does exist and it's a string, convert it to an array
          obj[paramName] = [obj[paramName]];
          obj[paramName].push(paramValue);
        } else {
          // otherwise add the property
          obj[paramName].push(paramValue);
        }
      }
    }
  }
  
  return obj;
}



function loadDoc() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          document.getElementById("lyrics").innerHTML =
          this.responseText;
     }
  };
  lyricstitle = getAllUrlParams(document.URL); 
  xhttp.open("GET", lyricstitle.song + ".lrc", true);
  xhttp.send();
}
function karaoke() {
  
  var xhttp = new XMLHttpRequest(); // Load lyrics
  var lyricstitle = {}
  listSongs()
  xhttp.onreadystatechange = function() {
   
   if (this.readyState == 4 && this.status == 200) {
    
     var text = xhttp.responseText;
     var lines = text.split("\n");
     linesCount = lines.length;
     
     for(i = 0; i < lines.length; i++){
       if (lines[i] != "") {
         var text = lines[i].replace(/ *\[[^)]*\] */g, ""); // Read lyric text
         var timing = lines[i].match(/\[([^)]+)\]/)[1]; // Read lyric timing
         var time = timing.split(':');
         var date = new Date();
         date.setMinutes(time[0]);
         var subTime = time[1].split('.');
         date.setSeconds(subTime[0]);
         date.setMilliseconds(subTime[1] * 10);
         dates[i] = date;
         var style;
         (i == 0) ? style = "highlight" : style = "plain";
         document.getElementById("lyrics").innerHTML += "<div class=\""+ style + "\" id=\"" + i + "\">" + text + "</div>"; // Add lyric to page
       }
     }
   }
  };
  console.log(document.URL);
  lyricstitle = getAllUrlParams(document.URL); 
  console.log(lyricstitle.song);
  xhttp.open("GET", "static/lyrics/" + lyricstitle.song + ".lrc", true);
  xhttp.send();

}

function start(url_id) {
  var player=document.getElementById('player');

  var sourceMp3=document.getElementById('player');
  
  sourceMp3.src="static/assets/music/" + url_id +".mp3";
    
  player.load(); //just start buffering (preload)
  player.play(); //start playing
  
  document.getElementById("player").controls = false;
  startSeconds = new Date().getTime(); // Song just started
  var nextTime = dates[0].getMinutes() * 60000 + dates[0].getSeconds() * 1000 + dates[0].getMilliseconds();
  setTimeout(function(){update(0, linesCount)}, nextTime); // Schedule first lyric update
  console.log('I was clicked')
  audioChunks = [];
  rec.start();
}

function update(current, last) {
  document.getElementById(current).className= "highlight"; // Update current lyric style
  if (current != 0) {
    document.getElementById(current - 1).className = "plain"; // Update previous lyric style
  }
  if (current++ < last) {
    var currentSeconds = new Date().getTime();
    var passedSeconds = currentSeconds - startSeconds;
    var nextTime = dates[current].getMinutes() * 60000 + dates[current].getSeconds() * 1000 + dates[current].getMilliseconds() - passedSeconds;
    setTimeout(function(){update(current, last)}, nextTime); // Schedule next lyric update
    if ( current >= 8 ){
      //window.scrollTo(0, (current -7) * 40);
      document.getElementById("lyrics").scrollTo(0, (current -7) * 40);
    }
  

  }

}




function handlerFunction(stream) {
rec = new MediaRecorder(stream);
rec.ondataavailable = e => {
  audioChunks.push(e.data);
  if (rec.state == "inactive"){
    let blob = new Blob(audioChunks,{type:'audio/mpeg-3'});
      recordedAudio.src = URL.createObjectURL(blob);
      recordedAudio.controls=true;
      recordedAudio.autoplay=true;
      sendData(blob)


  }
}
}

function listSongs() {
  var rawFile = new XMLHttpRequest(); // XMLHttpRequest (often abbreviated as XHR) is a browser object accessible in JavaScript that provides data in XML, JSON, but also HTML format, or even a simple text using HTTP requests.
    rawFile.open("GET", "static/songs.txt", false); // open with method GET the file with the link file ,  false (synchronous)
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4) // readyState = 4: request finished and response is ready
        {
            if(rawFile.status === 200) // status 200: "OK"
            {
                var allText = rawFile.responseText; //  Returns the response data as a string

                var mynewtext = allText.split("\n")
                mynewtext.forEach(function (item) {
                  myarr = item.split("#")
                  var songnames=myarr.shift();
                  var vidid=myarr.pop();
                  document.getElementById("Mysongs").innerHTML += "<li><a href='?song=" + vidid + "'>" + songnames + "</a></li>"
                })
            }
        }
    }
    rawFile.send(null);
  

 
  
  
}

function sendData(data) {}

function loadSong(){
    
    
}

function ProcessYT() {
  var linkvalue = document.getElementById('ytlink').value;
  window.location.href = 'http://localhost:9094/ytprocess?link=' + linkvalue;
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      window.location.href = 'http://localhost:9094/acknowledge';
    }
  };
  xhttp.open("POST", "acknowledge.html", true);
  xhttp.send();
}
