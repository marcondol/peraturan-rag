# Catatan Sidekiq vs Kafka (dokumen contoh untuk retrieval pertama)

## Sidekiq

Sidekiq adalah background job processor untuk aplikasi Ruby/Rails.
Job diserialisasi jadi JSON dan dimasukkan ke antrean di Redis, lalu
proses Sidekiq terpisah mengambil dan menjalankannya di worker thread.
Job yang selesai hilang dari antrean; job gagal di-retry otomatis
dengan backoff, default 25 kali selama sekitar 3 minggu, lalu masuk
dead queue. Di GitLab, Sidekiq adalah pemroses background job utama.

## Kafka

Kafka menyimpan fakta kejadian dalam distributed log di disk dengan
replikasi. Satu event bisa dibaca banyak consumer group secara
independen dan bisa di-replay. Kafka menjamin urutan di dalam satu
partition, tapi tidak punya retry per pesan bawaan.

## Perbedaan inti

Sidekiq mengantre perintah kerja ("kirim invoice ini"); Kafka mencatat
fakta ("invoice sudah diterbitkan"). Sidekiq: satu job dikerjakan satu
worker. Kafka: satu event dibaca banyak consumer. Batas scaling Kafka
adalah jumlah partisi; batas scaling Sidekiq adalah pool koneksi
database, GVL Ruby untuk kerja berat CPU, dan Redis/CPU.
