fetch("/Api/sumario/grafiku/faze/")
.then(response => response.json())
.then(data => {

    new Chart(document.getElementById('fazeChart'), {
        type: 'bar', // Tipe dasar grafik adalah bar
        data: {
            labels: data.label,
            datasets: [
                {
                    type: 'bar', // Dataset pertama berupa BAR
                    label: 'Total (Bar)',
                    data: data.obj,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    type: 'line', // Dataset kedua berupa LINE
                    label: 'Tren (Line)',
                    data: data.obj, // Menggunakan data yang sama, atau ganti dengan array data lain jika ada
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 2,
                    fill: false, // Set true jika ingin area di bawah garis berwarna
                    tension: 0.1 // Membuat garis sedikit melengkung
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Mengizinkan grafik mengikuti tinggi elemen pembungkus (parent)
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

});
