Memilah Data Produk Bhinneka
============================
Aplikasi ini berguna untuk memilah produk yang ada di bhinneka.com. Tujuan
akhirnya memudahkan pencarian produk seperti: "Dapatkan harga notebook maksimal
Rp 5.000.000".

Dibutuhkan scrapy untuk menjalankannya. Sudah teruji di Scrapy 1.0.3.

Pemasangan
----------
Buatlah Python virtual environment::

  virtualenv env

Lalu pasanglah scrapy::

  env/bin/pip install -r bhinneka/requirements.txt

Tidak ada pemasangan driver database di sini.

Pengambilan Data
----------------
Data yang diambil akan disimpan dalam sebuah file bertipe JSON.
Untuk mengambil daftar produk notebook::

  cd bhinneka
  ../env/bin/scrapy crawl notebook -t json -o notebook.json

untuk handphone::

  ../env/bin/scrapy crawl mobile_phone -t json -o mobile_phone.json

dan untuk komputer desktop::

  ../env/bin/scrapy crawl desktop -t json -o deskt.json

Dari file JSON ini kita bisa lanjutkan ke penyimpanan database, sesuai
selera masing-masing. Silahkan.
