5350 _33_ 1d - 81 01 *40* = *40* _33_

00110011 00011101 10000001 00000001 01000000

 _A0_ 1E -81 01 *40* = *40* _A0_

A b - c d E => type E:A.

b är 1e eller 1d. c + d är alltid 81 01.

Display Resolution: 1 ATC_GICISKY_Paper_Image_Upload.html:347:21
Display Type: 2 ATC_GICISKY_Paper_Image_Upload.html:348:21
Display Colors: 1 ATC_GICISKY_Paper_Image_Upload.html:349:21
Display Mirror: 1 ATC_GICISKY_Paper_Image_Upload.html:350:21
Display Compression: 0 ATC_GICISKY_Paper_Image_Upload.html:351:21

min:
0 1 0 0 0 0 0 0:0 0 1 1 0 0 1 1
f e d c b a 9 8:7 6 5 4 3 2 1 0
  x C C   r r r:r r r t t c c m

                case 0:
                    document.getElementById('widthInput').value = "104";
                    document.getElementById('heightInput').value = "212";
                    break;
                case 8:
                    document.getElementById('widthInput').value = "128";
                    document.getElementById('heightInput').value = "250";
                    break;

                case 1:
                    document.getElementById('widthInput').value = "128";
                    document.getElementById('heightInput').value = "296";
                    break;
                case 9:
                    document.getElementById('widthInput').value = "800";
                    document.getElementById('heightInput').value = "480";
                    break;

                case 2:
                    document.getElementById('widthInput').value = "400";
                    document.getElementById('heightInput').value = "300";
                    break;
                case 10:
                    document.getElementById('widthInput').value = "480";
                    document.getElementById('heightInput').value = "280";
                    break;

                case 3:
                    document.getElementById('widthInput').value = "384";
                    document.getElementById('heightInput').value = "640";
                    break;
                case 4:
                    document.getElementById('widthInput').value = "640";
                    document.getElementById('heightInput').value = "960";
                    break;
                case 5:
                    document.getElementById('widthInput').value = "132";
                    document.getElementById('heightInput').value = "250";
                    break;
                case 6:
                    document.getElementById('widthInput').value = "96";
                    document.getElementById('heightInput').value = "196";
                    break;
                case 7:
                    document.getElementById('widthInput').value = "480";
                    document.getElementById('heightInput').value = "640";
                    break;
            }

// C C är eg bara ". C", och om C är == 1 och "c c" är 0 0, så klarar den "BWRGBYO"
        function decodeTypes(rawType) {
            var screenResolution = (rawType >> 5) & 63; // r
            var dispPtype = (rawType >> 3) & 3; // t
            var availColors = ((rawType >> 1) & 3) + ((rawType >> 10) & 12); // c and C ((starting at 4))
            var singleDoubleMirror = rawType & 1; // m
            var canDoCompression = (rawType & 0x4000) ? 0 : 1; // x

            console.log("Display Resolution: " + screenResolution);
            console.log("Display Type: " + dispPtype);
            console.log("Display Colors: " + availColors);
            console.log("Display Mirror: " + singleDoubleMirror);
            console.log("Display Compression: " + canDoCompression);


            if (canDoCompression)
                document.getElementById('compressionCheckbox').checked = true;
            else
                document.getElementById('compressionCheckbox').checked = false;


            switch (screenResolution) {
                case 0:
                    document.getElementById('widthInput').value = "104";
                    document.getElementById('heightInput').value = "212";
                    break;
                case 1:
                    document.getElementById('widthInput').value = "128";
                    document.getElementById('heightInput').value = "296";
                    break;
                case 2:
                    document.getElementById('widthInput').value = "400";
                    document.getElementById('heightInput').value = "300";
                    break;
                case 3:
                    document.getElementById('widthInput').value = "384";
                    document.getElementById('heightInput').value = "640";
                    break;
                case 4:
                    document.getElementById('widthInput').value = "640";
                    document.getElementById('heightInput').value = "960";
                    break;
                case 5:
                    document.getElementById('widthInput').value = "132";
                    document.getElementById('heightInput').value = "250";
                    break;
                case 6:
                    document.getElementById('widthInput').value = "96";
                    document.getElementById('heightInput').value = "196";
                    break;
                case 7:
                    document.getElementById('widthInput').value = "480";
                    document.getElementById('heightInput').value = "640";
                    break;
                case 8:
                    document.getElementById('widthInput').value = "128";
                    document.getElementById('heightInput').value = "250";
                    break;
                case 9:
                    document.getElementById('widthInput').value = "800";
                    document.getElementById('heightInput').value = "480";
                    break;
                case 10:
                    document.getElementById('widthInput').value = "480";
                    document.getElementById('heightInput').value = "280";
                    break;
            }

            switch (dispPtype) {
                case 0:// TFT
                    document.getElementById('mirrorCheckbox').checked = true;
                    break;
                case 1:// EPA
                    document.getElementById('mirrorCheckbox').checked = true;
                    break;
                case 2:// EPA1
                    document.getElementById('mirrorCheckbox').checked = false;
                    break;
                case 3:// EPA2
                    document.getElementById('mirrorCheckbox').checked = true;
                    break;
            }
            switch (availColors) {
                case 0:// BW
                    document.getElementById('secondColorCheckbox').checked = false;
                    break;
                case 1:// BWR
                    document.getElementById('secondColorCheckbox').checked = true;
                    break;
                case 2:// BWY
                    document.getElementById('secondColorCheckbox').checked = true;
                    break;
                case 3:// BWRY
                    document.getElementById('secondColorCheckbox').checked = true;
                    break;
                case 4:// BWRGBYO
                    document.getElementById('secondColorCheckbox').checked = true;
                    break;
            }
            switch (singleDoubleMirror) {
                case 0:// Single image
                    break;
                case 1:// 2 Images
                    break;
            }

4109:
Display Resolution: 8 ATC_GICISKY_Paper_Image_Upload.html:347:21
Display Type: 1 ATC_GICISKY_Paper_Image_Upload.html:348:21
Display Colors: 0 ATC_GICISKY_Paper_Image_Upload.html:349:21
Display Mirror: 1 ATC_GICISKY_Paper_Image_Upload.html:350:21
Display Compression: 0

410B:
Display Resolution: 8 ATC_GICISKY_Paper_Image_Upload.html:347:21
Display Type: 1 ATC_GICISKY_Paper_Image_Upload.html:348:21
Display Colors: 1 ATC_GICISKY_Paper_Image_Upload.html:349:21
Display Mirror: 1 ATC_GICISKY_Paper_Image_Upload.html:350:21
Display Compression: 0

0129:
Display Resolution: 9 ATC_GICISKY_Paper_Image_Upload.html:347:21
Display Type: 1 ATC_GICISKY_Paper_Image_Upload.html:348:21
Display Colors: 0 ATC_GICISKY_Paper_Image_Upload.html:349:21
Display Mirror: 1 ATC_GICISKY_Paper_Image_Upload.html:350:21
Display Compression: 1

4109:
Display Resolution: 8 ATC_GICISKY_Paper_Image_Upload.html:347:21
Display Type: 1 ATC_GICISKY_Paper_Image_Upload.html:348:21
Display Colors: 0 ATC_GICISKY_Paper_Image_Upload.html:349:21
Display Mirror: 1 ATC_GICISKY_Paper_Image_Upload.html:350:21
Display Compression: 0 ATC_GICISKY_Paper_Image_Upload.html:351:21


            <option value="4109">250x122 BW</option>
            <option value="410B">250x122 BWR</option>
            <option value="0129">800x480 BW</option>
            <option value="012B">800x480 BWR</option>
            <option value="0030">296x128 BW</option>
            <option value="0032">296x128 BWR</option>
            <option value="0049">400x300 BW</option>
            <option value="004B">400x300 BWR</option>
            <option value="40A0">250x132 TFT</option>


            <option value="Not Added">212x104 BW</option>
            <option value="Not Added">212x104 BWR</option>
            <option value="0030">296x128 BW</option>
            <option value="0032">296x128 BWR</option>
            <option value="0049">400x300 BW</option>
            <option value="004B">400x300 BWR</option>
            <option value="Not Added">640x384 BW</option>
            <option value="Not Added">640x384 BWR</option>
            <option value="Not Added">960x640 BW</option>
            <option value="Not Added">960x640 BWR</option>
            <option value="40A0">250x132 TFT</option>
            <option value="Not Added">196x96 BW</option>
            <option value="Not Added">196x96 BWR</option>
            <option value="Not Added">640x480 BW</option>
            <option value="Not Added">640x480 BWR</option>
            <option value="4109">250x122 BW</option>
            <option value="410B">250x122 BWR</option>
            <option value="0129">800x480 BW</option>
            <option value="012B">800x480 BWR</option>
            <option value="Not Added">280x480 BW</option>
            <option value="Not Added">280x480 BWR</option>
