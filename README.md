# FabBits
FabBits is a standalone cross-platform software capable of finding certain interesting bits from movies/shows, soccer, and basketball. Following are the things it will be able to detect -

* Action sequences in movies/shows  - ✅
* Summary of movies/shows - ✅
* Actor-specific scenes in movies/shows - ✅
* Jokes in sitcoms - ✅
* Slo-mos in Sports - ❌
* Goals in Soccer - ✅
* Goal misses in Soccer - ⭕
* Three pointers in Basketball - ⭕

## Requirements
You need the following things to run FabBits -

1. [Python3](https://www.python.org/download/releases/3.0/) 
2. [OpenCV](https://opencv.org) - Used for image and video processing
3. [Moviepy](https://zulko.github.io/moviepy/) - Used for video editing and audio processing
4. [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) - Used to make the GUI
5. [Scipy](https://www.riverbankcomputing.com/software/pyqt/intro) - Used for audio processing

The python dependencies can be installed by running - 
```
pip3 install scipy
pip3 install opencv-python
pip3 install moviepy
pip3 install pyqt5
```

or if you are the Anaconda kind -
```
conda install -c conda-forge scipy
conda install -c conda-forge opencv
conda install -c conda-forge moviepy
conda install -c anaconda pyqt 
```
## Usage
Once that's done, run the main GUI by -
<code>python3 main.py</code>

To find your FabBit of choice -
* Click `MOVIES` or `SPORTS` button for their respective use-cases
* Select the use-case from the sidebar
	* A pop-up dialog will ask for the actor if actor-specific scene was chosen
* Click on `Choose File` to select the input video 
* Click on `Find FabBits`
* Move the slider in the blue areas, which are the extracted FabBits, and play the video
* Click on `Save FabBits` to save the extracted stuff into a video file

You can also run the respective files of use-cases to get their FabBit, like -
<code>python3 goal_detector.py soccer_match.mp4</code>

## Contributing
Pull requests are welcome! Although for major changes, please open an issue first to discuss what you would like to change.

## References
[Audio-Based Action Scene Classification Using HMM-SVM Algorithm by Khin Myo Chit, K Zin Lin](http://ijarcet.org/wp-content/uploads/IJARCET-VOL-2-ISSUE-4-1347-1351.pdf)

[Action Scene Detection with Support Vector Machines; Liang-Hua Chen, Chih-Wen Su et a](https://pdfs.semanticscholar.org/2a20/0432f71bf19c8efe19b686799e94226e2d32.pdf)

[A Scoreboard Based Method for Goal events Detecting in Football Videos; Song Yang, Wen Xiangming et al](https://www.researchgate.net/publication/252020501_A_Scoreboard_Based_Method_for_Goal_Events_Detecting_in_Football_Videos)

[Detecting Soccer Goal Scenes from Broadcast Video using Telop Region;
Naoki Ueda, Masao Izumi](http://www.iaiai.org/journals/index.php/IEE/article/view/187)

[Anatomy of a Laugh Track](https://archive.cnx.org/contents/a7ec0ec7-9093-4f55-93ef-3ac2ce71b1c8@3/anatomy-of-a-laugh-track)

[Primary Detection Methods for Laugh Tracks](https://archive.cnx.org/contents/8ffeeb0f-fb40-4d3e-a63f-aaff422f9eab@2/primary-detection-methods-for-laugh-tracks)

[Real-Time Event Detection in Field Sport Videos](https://pdfs.semanticscholar.org/b759/21d79a144e419f6fe71a06f65f26a51f6b44.pdf)

[Finding Celebrities in Billions of Webpages; Xiao Zhang, Lei Zhang, Xin-Jing Wang, Heung-Yeung Shum; IEEE Transaction on Multimedia, 2012](https://www.microsoft.com/en-us/research/project/msra-cfw-data-set-of-celebrity-faces-on-the-web/)

[C.H. Demarty,C. Penet, M. Soleymani, G. Gravier. VSD, a public dataset for the detection of violent scenes in movies: design, annotation, analysis and evaluation. In Multimedia Tools and Applications, May 2014](http://link.springer.com/article/10.1007/s11042-014-1984-4)

[C.H. Demarty, B. Ionescu, Y.G. Jiang, and C. Penet. Benchmarking Violent Scenes Detection in movies. In Proceedings of the 2014 12th International Workshop on Content-Based Multimedia Indexing (CBMI), 2014](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?reload=true&arnumber=6849827&abstractAccess=no&userType=inst)

[M. Sjöberg, B. Ionescu, Y.G. Jiang, V.L. Quang, M. Schedl and C.H. Demarty. The MediaEval 2014 Affect Task: Violent Scenes Detection. In Working Notes Proceedings of the MediaEval 2014 Workshop, Barcelona, Spain (2014)](http://ceur-ws.org/Vol-1263/mediaeval2014_submission_3.pdf)

[C.H. Demarty,C. Penet, G. Gravier and M. Soleymani. A benchmarking campaign for the multimodal detection of violent scenes in movies.In Proceedings of the 12thinternational conference on Computer Vision – Volume Part III (ECCV’12),Andrea Fusiello, Vittorio Murino, and Rita Cucchiara (Eds), Col. Part III. Springer Verlag, Berlin](http://ibug.doc.ic.ac.uk/media/uploads/documents/demarty_eccvw2012_finalversion.pdf)