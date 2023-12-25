安装依赖库
==========

    apt install libtool
    apt install libicu-dev
    apt install libtiff-dev
    apt install libpango1.0-dev

    yum install libicu-devel
    yum install libtiff-devel
    yum install pango-devel

安装leptonica
==========

    wget https://github.com/DanBloomberg/leptonica/releases/download/1.83.1/leptonica-1.83.1.tar.gz

    tar vxzf leptonica-1.83.1.tar.gz
    cd leptonica-1.83.1

    ./configure
    make
    make install

    export LD_LIBRARY_PATH=$LD_LIBRARY_PAYT:/usr/local/lib
    export LIBLEPT_HEADERSDIR=/usr/local/include
    export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

安装tesseract
==========

    wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.3.3.tar.gz

    tar vxzf 5.3.3.tar.gz
    cd tesseract-5.3.3

    ./autogen.sh
    ./configure --prefix=/opt/tesseract
    make training
    make install
    make training-install

wget
==========

    wget https://github.com/tesseract-ocr/tessdata_best/archive/refs/tags/4.1.0.tar.gz

    tar vxzf 4.1.0.tar.gz
    mv tessdata_best-4.1.0 tessdata_best

    wget https://codeload.github.com/tesseract-ocr/langdata_lstm/zip/refs/heads/main

    unzip main
    mv langdata_lstm-main langdata_lstm
