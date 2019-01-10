::Install Python Modules
D:\Anaconda2\python -m pip install -r requirements.txt

::Install Ta-Lib
D:\Anaconda2\python -m conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
D:\Anaconda2\python -m conda config --set show_channel_urls yes
D:\Anaconda2\python -m conda install -c quantopian ta-lib=0.4.9 -y

:: Install vn.py
D:\Anaconda2\python setup.py install