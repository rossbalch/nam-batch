This is a version of https://github.com/sdatkinson/neural-amp-modeler that has a batch script so you can queue training.

Using the batch script is fairly simple, but there are some setup rules you will need to follow.

Installing is easy, first follow the install instruction for the original neural-amp-modeler if you haven't already, then install my custom repo that contains the batch process

briefly:
Install Conda
using conda install git if you don't have it already

```bash
conda install git
```
```bash
git clone https://github.com/sdatkinson/neural-amp-modeler
```
```bash
cd neural-amp-modeler
```
```bash
conda env create -f environment_gpu.yml
```
```bash
python setup.py install
```

```bash
cd ..
```
```bash
git clone https://github.com/rossbalch/nam-batch
```

# Usage
Copy your input and output files to the materials folder in the nam-batch directory. It is important that you copy the files and not move them, the files will be deleted after the process finishes. There are also some naming considerations. Your files must be called name_In.wav and name_Out.wav the batch script will not recognise them other wise. </br>
For Instance: </br>
Peavy_5150_In.wav </br?
Peavy_5150_Out.wav </br>
If you use the original v_1_1_1 file just copy and rename it for each model you wish to train. </br>
Once all the files you wish to train are in the materials folder simply run the script, it will ascertain the delay, queue up the training, generate the models and all the resulting files will be available in the exports folder. </br>

```bash
cd nam-batch
```
```bash
conda activate nam
```
```bash
python batch.py
```


