Memilah Data Produk Bhinneka 
============================
Aplikasi ini berguna untuk memilah produk yang ada di Bhinneka_. Tujuan
akhirnya memudahkan pencarian produk seperti: "Dapatkan harga notebook maksimal
Rp 5.000.000".

Dibutuhkan scrapy untuk menjalankannya. Sudah teruji di Scrapy 1.0.3.

Pemasangan
----------
Siapkan pustaka yang dibutuhkan::

  sudo apt-get install libxml2-dev libxslt1-dev python-dev libffi-dev

Buatlah Python virtual environment::

  virtualenv env

Setelah source ``bhinneka`` ini diunduh lalu pasanglah ``scrapy``::

  env/bin/pip install -r bhinneka/requirements.txt

Tidak ada pemasangan driver database di sini.

Pengambilan Data
----------------
Data yang diambil akan disimpan dalam sebuah file bertipe JSON.
Untuk mengambil daftar produk notebook::

  mkdir -p /home/webdate/tmp/bhinneka
  cd bhinneka 
  ../env/bin/scrapy crawl notebook -t json \
      -o /home/webdate/tmp/bhinneka/notebook.json
  
Jika Anda ingin menyimpan file HTML setiap produk di sebuah direktori gunakan
Spider_Arguments_ ``-a save_dir=/path/target``. Tapi sebelumnya
hapuslah file ``notebook.json`` agar tidak membengkak::

  rm -f /home/webdate/tmp/bhinneka/notebook.json
  mkdir -p /home/webdate/tmp/bhinneka/notebook
  ../env/bin/scrapy crawl notebook -t json \
      -o /home/webdate/tmp/bhinneka/notebook.json
      -a save_dir=/home/webdate/tmp/bhinneka/notebook

Merasa ada penerjemahan yang kurang pas ? Setelah Anda memperbaiki source maka
file HTML tadi bisa dibaca kembali, jadi tidak perlu unduh ulang::

  ../env/bin/scrapy crawl notebook -t json \
      -o /home/webdate/tmp/bhinneka/notebook.json
      -a product_url=file:///home/webdate/tmp/bhinneka/notebook

Apakah pengambilan data produk tertentu ada yang kurang pas ? Perbaikilah source-nya.
Setelah itu Anda bisa unduh halaman produk itu saja agar lebih cepat, sekedar memastikan
apakah perbaikan sudah sesuai::

  ../env/bin/scrapy crawl notebook -t json \
      -a product_url=http://www.bhinneka.com/products/sku01915977/dell_inspiron_14_3451__pentium_n3540__-_black.aspx
 
Bisa juga HTML bersumber dari *cache*::

  ../env/bin/scrapy crawl notebook -t json \
      -a product_url=file:///home/webdate/tmp/bhinneka/notebook/dell_inspiron_14_3451__pentium_n3540__-_black.aspx

Jika sudah pas jalankan kembali perintah sebelumnya agar seluruh produk diproses ulang::

  rm -f /home/webdate/tmp/bhinneka/notebook.json
  ../env/bin/scrapy crawl notebook -t json \
      -o /home/webdate/tmp/bhinneka/notebook.json
      -a product_url=file:///home/webdate/tmp/bhinneka/notebook

Biasanya sebuah toko online akan memperbaharui datanya setiap hari. Oleh karena
itu kita perlu meletakkan perintah ini pada sistem *cron*. Untuk pemantauan
aktivitasnya diperlukan pencatatan ke *log file*::

  rm -f /home/webdate/tmp/bhinneka/notebook.json
  rm -f /home/webdate/tmp/bhinneka/notebook.log
  cd /home/webdate/bhinneka 
  ../env/bin/scrapy crawl notebook -t json \
      -o /home/webdate/tmp/bhinneka/notebook.json
      -a save_dir=/home/webdate/tmp/bhinneka/notebook \
      --logfile=/home/webdate/tmp/bhinneka/notebook.log

Selanjutnya kita bisa akhiri script di atas dengan script penyalin ke database
bersumber dari ``notebook.json``.

Selain kategori ``notebook`` yang tersedia adalah ``mobile_phone`` dan ``desktop``.

Silahkan dicoba.

.. _Bhinneka: http://bhinneka.com
.. _Spider_Arguments: http://doc.scrapy.org/en/latest/topics/spiders.html#spider-arguments
