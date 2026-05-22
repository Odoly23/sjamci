import hashlib
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages

class SecurityAndCacheMiddleware(MiddlewareMixin):
    """
    Middleware untuk mengatur Cache Control secara global (Mencegah Tombol Back setelah Logout)
    dan mengarahkan user terautentikasi agar tidak bisa kembali ke halaman login.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if request.path == reverse('login'):
                return redirect('/')
        return None

    def process_response(self, request, response):
        # Mencegah browser menyimpan cache di memori lokal (Solusi mutlak tombol Back)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class PreventDuplicatePostMiddleware:
    """
    Middleware otomatis untuk mendeteksi Double Submit dan manipulasi tombol Back pada form POST.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Simpan URL asal yang valid sebelum memproses request saat ini
        if request.method == 'GET':
            # Jangan simpan URL jika itu berasal dari referer eksternal atau kosong
            referer = request.META.get('HTTP_REFERER')
            if referer and request.get_host() in referer:
                request.session['safe_previous_url'] = referer

        if request.method == 'POST':
            # 1. Hitung struktur data kiriman untuk mendeteksi kesamaan konten
            file_info = ''
            if request.FILES:
                file_info = str(sorted([(k, v.name, v.size) for k, v in request.FILES.items()]))
            
            post_data_str = request.path + str(sorted(request.POST.items())) + file_info
            post_hash = hashlib.sha256(post_data_str.encode()).hexdigest()
            
            last_hash = request.session.get('last_post_hash')
            last_path = request.session.get('last_post_path')

            # 2. Jika Hash dan Path sama persis, berarti ini kiriman duplikat (Double Click / Back-Submit)
            if last_hash == post_hash and last_path == request.path:
                previous_url = request.session.get('safe_previous_url') or '/'
                messages.warning(request, 'Dadus rejistadu ona. La bele submete fila fali.')
                return redirect(previous_url)

            # 3. Jika kiriman baru dan sah, simpan signature hash ke session
            request.session['last_post_hash'] = post_hash
            request.session['last_post_path'] = request.path

        response = self.get_response(request)

        # 4. KUNCI UTAMA: Jika POST berhasil dan melakukan redirect (302), langsung bersihkan hash
        # Ini agar user bisa langsung mengisi form baru lagi tanpa diblokir oleh hash sebelumnya.
        if request.method == 'POST' and response.status_code == 302:
            request.session.pop('last_post_hash', None)
            request.session.pop('last_post_path', None)

        return response
