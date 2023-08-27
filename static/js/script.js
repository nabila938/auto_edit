$(document).ready(function () {
    if(window.location.pathname == '/') {
        getUser();
        getTugas();
    }
})

function getUser() {
    $.ajax({
        type: 'GET',
        url: '/getData?collection=user',
        data: {},
        success: response => {
            response.forEach(user => {
                temp_html = `<option value="${user.username}">${user.username}</option>`;
                $('#select-user').append(temp_html);
            });
        }
    })
}

function getTugas() {
    $.ajax({
        type: 'GET',
        url: '/getData?collection=file_tugas',
        data: {},
        success: response => {
            response.forEach(file => {
                temp_html = `
                <div class="container my-2">
                    <div class="row border d-flex align-items-center py-1 shadow mx-1">
                    <div class="col">
                        <span class="d-block"> ${file.tugasName}</span>
                        <span class="d-block" style="font-size: 0.6rem;">${file.keterangan}</span>
                    </div>
                    <div class="col text-end">
                        <button type="submit" value="${file.fileName}" class="btn btn-success download-tugas">Download</button>
                    </div>
                    </div>
                </div>
                `;
                $('#file-tugas').append(temp_html);
            });
        }
    });
}

// Menggunakan event delegation untuk menangani klik tombol-tombol yang ditambahkan secara dinamis
$('#file-tugas').on('click', '.btn-success', function() {
    var fileName = $(this).val();
    const selectedUser = $('#select-user').val();
    console.log(selectedUser, fileName)

    if( selectedUser !== 'Pilih User') {

        $.ajax({
            type: 'POST',
            url: '/download',
            data : {
              'user': selectedUser,
              'tugas': fileName
            },
            success: function(response) {
                console.log(response)
                alert(response.msg);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("Error:", textStatus, errorThrown);
            }     
        });
    } else {
        alert('silahkan pilih user')
        return;
    }
});

// function downloadTugas() {
//     $('.download-tugas').click(function() {
//         const selectedUser = $('#select-user').val();
//         const tugasName = $(this).val(); // Nilai dari tombol yang diklik

//         // Kirim data menggunakan AJAX
//         $.ajax({
//             type: 'POST',
//             url: '/test',
//             contentType: 'application/json',
//             data: JSON.stringify({
//                 user: selectedUser,
//                 tugas: tugasName
//             }),
//             success: function(response) {
//                 console.log('Berhasil mendownload', response.msg);
//             },
//             error: function() {
//                 console.error('Terjadi kesalahan saat mendownload');
//             }
//         });
//     });
// }