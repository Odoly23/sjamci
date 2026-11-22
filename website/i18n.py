"""Tradusaun pajina públiku iha lian 4: Tetun, Português, English, Bahasa Indonesia."""

LANGUAGES = [
    ('tet', 'Tetun', 'tl'),
    ('pt', 'Português', 'pt'),
    ('en', 'English', 'gb'),
    ('id', 'Bahasa Indonesia', 'id'),
]
DEFAULT = 'tet'
CODES = [code for code, _name, _flag in LANGUAGES]

_T = {
    'ministry': {
        'tet': 'Ministériu Komérsiu no Indústria', 'pt': 'Ministério do Comércio e Indústria',
        'en': 'Ministry of Commerce and Industry', 'id': 'Kementerian Perdagangan dan Industri'},
    'system_name': {
        'tet': 'Sistema Jestaun Apoiu MCI', 'pt': 'Sistema de Gestão de Apoios do MCI',
        'en': 'MCI Support Management System', 'id': 'Sistem Manajemen Bantuan MCI'},
    'skip': {'tet': 'Ba konteúdu prinsipál', 'pt': 'Ir para o conteúdo principal',
             'en': 'Skip to main content', 'id': 'Lompat ke konten utama'},
    'lang_label': {'tet': 'Hili lian', 'pt': 'Escolher idioma', 'en': 'Choose language', 'id': 'Pilih bahasa'},
    'menu': {'tet': 'Menu', 'pt': 'Menu', 'en': 'Menu', 'id': 'Menu'},
    'nav_home': {'tet': 'Inísiu', 'pt': 'Início', 'en': 'Home', 'id': 'Beranda'},
    'nav_programs': {'tet': 'Programa', 'pt': 'Programas', 'en': 'Programmes', 'id': 'Program'},
    'nav_stats': {'tet': 'Estatístika', 'pt': 'Estatísticas', 'en': 'Statistics', 'id': 'Statistik'},
    'nav_info': {'tet': 'Informasaun', 'pt': 'Informação', 'en': 'Information', 'id': 'Informasi'},
    'nav_features': {'tet': 'Funsionalidade', 'pt': 'Funcionalidades', 'en': 'Features', 'id': 'Fitur'},
    'nav_faq': {'tet': 'Pergunta', 'pt': 'Perguntas', 'en': 'FAQ', 'id': 'Tanya Jawab'},
    'nav_contact': {'tet': 'Kontaktu', 'pt': 'Contacto', 'en': 'Contact', 'id': 'Kontak'},
    'login': {'tet': 'Tama Sistema', 'pt': 'Entrar no Sistema', 'en': 'Sign in', 'id': 'Masuk Sistem'},

    'slide1_title': {
        'tet': 'Apoiu ba negósiu no indústria iha Timor-Leste tomak',
        'pt': 'Apoio ao comércio e à indústria em todo o Timor-Leste',
        'en': 'Supporting business and industry across Timor-Leste',
        'id': 'Mendukung usaha dan industri di seluruh Timor-Leste'},
    'slide1_sub': {
        'tet': 'Sistema ida de\'it atu rejista, akompaña no avalia benefisiáriu programa MCI.',
        'pt': 'Um único sistema para registar, acompanhar e avaliar os beneficiários dos programas do MCI.',
        'en': 'One system to register, follow up and evaluate beneficiaries of MCI programmes.',
        'id': 'Satu sistem untuk mendaftarkan, mendampingi, dan mengevaluasi penerima manfaat program MCI.'},
    'slide2_title': {
        'tet': 'Dadus husi munisípiu hotu, atualiza husi ofisiál iha terrenu',
        'pt': 'Dados de todos os municípios, atualizados pelos oficiais no terreno',
        'en': 'Data from every municipality, updated by officers in the field',
        'id': 'Data dari semua munisipiu, diperbarui petugas di lapangan'},
    'slide2_sub': {
        'tet': 'Rejistu bele halo maski la iha internet no sinkroniza bainhira rede iha fali.',
        'pt': 'O registo pode ser feito sem internet e sincronizado quando a rede voltar.',
        'en': 'Registration works without internet and syncs when the connection returns.',
        'id': 'Pendaftaran bisa dilakukan tanpa internet dan tersinkron saat jaringan kembali.'},
    'slide3_title': {
        'tet': 'Transparénsia: estatístika benefisiáriu loke ba públiku',
        'pt': 'Transparência: estatísticas de beneficiários abertas ao público',
        'en': 'Transparency: beneficiary statistics open to the public',
        'id': 'Transparansi: statistik penerima manfaat terbuka untuk publik'},
    'slide3_sub': {
        'tet': 'Haree númeru benefisiáriu tuir munisípiu, tinan no programa.',
        'pt': 'Consulte o número de beneficiários por município, ano e programa.',
        'en': 'See beneficiary numbers by municipality, year and programme.',
        'id': 'Lihat jumlah penerima manfaat per munisipiu, tahun, dan program.'},
    'cta_stats': {'tet': 'Haree estatístika', 'pt': 'Ver estatísticas', 'en': 'View statistics', 'id': 'Lihat statistik'},
    'slide_prev': {'tet': 'Slide uluk', 'pt': 'Slide anterior', 'en': 'Previous slide', 'id': 'Slide sebelumnya'},
    'slide_next': {'tet': 'Slide tuir mai', 'pt': 'Slide seguinte', 'en': 'Next slide', 'id': 'Slide berikutnya'},
    'slide_pause': {'tet': 'Para slide', 'pt': 'Pausar slides', 'en': 'Pause slides', 'id': 'Jeda slide'},
    'slide_play': {'tet': 'Kontinua slide', 'pt': 'Retomar slides', 'en': 'Resume slides', 'id': 'Lanjutkan slide'},

    'kpi_benef': {'tet': 'Benefisiáriu simu apoiu', 'pt': 'Beneficiários apoiados',
                  'en': 'Beneficiaries supported', 'id': 'Penerima manfaat didukung'},
    'kpi_business': {'tet': 'Negósiu apoiadu', 'pt': 'Negócios apoiados', 'en': 'Businesses supported', 'id': 'Usaha didukung'},
    'kpi_mun': {'tet': 'Munisípiu kobre', 'pt': 'Municípios abrangidos', 'en': 'Municipalities covered', 'id': 'Munisipiu terjangkau'},
    'kpi_groups': {'tet': 'Grupu manufatureira (DNIM)', 'pt': 'Grupos da indústria transformadora (DNIM)',
                   'en': 'Manufacturing groups (DNIM)', 'id': 'Kelompok manufaktur (DNIM)'},
    'kpi_enterprises': {'tet': 'Empreza rejistadu (MPMS)', 'pt': 'Empresas registadas (MPMS)',
                        'en': 'Registered enterprises (MPMS)', 'id': 'Perusahaan terdaftar (MPMS)'},
    'kpi_programs': {'tet': 'Apoiu atribui', 'pt': 'Apoios atribuídos', 'en': 'Support grants recorded', 'id': 'Bantuan tercatat'},

    'programs_title': {'tet': 'Programa sira', 'pt': 'Programas', 'en': 'Programmes', 'id': 'Program'},
    'programs_lead': {
        'tet': 'Sistema jere programa apoiu haat husi diresaun sira iha MCI.',
        'pt': 'O sistema gere quatro programas de apoio das direções do MCI.',
        'en': 'The system manages four support programmes run by MCI directorates.',
        'id': 'Sistem ini mengelola empat program bantuan dari direktorat-direktorat MCI.'},
    'prog_kni': {
        'tet': 'Rejistu benefisiáriu no negósiu, apoiu tuir faze, sertifikadu no monitorizasaun impaktu.',
        'pt': 'Registo de beneficiários e negócios, apoio por fases, certificado e monitorização de impacto.',
        'en': 'Beneficiary and business registration, phased support, certificates and impact monitoring.',
        'id': 'Pendaftaran penerima manfaat dan usaha, bantuan bertahap, sertifikat, dan pemantauan dampak.'},
    'prog_ks_name': {'tet': 'Kreditu Suave', 'pt': 'Crédito Suave', 'en': 'Soft Credit', 'id': 'Kredit Lunak'},
    'prog_ks': {
        'tet': 'Akompañamentu kréditu ba empreza: ekipa, produtu, merkadu, finansas no pagamentu.',
        'pt': 'Acompanhamento de crédito a empresas: equipa, produtos, mercado, finanças e reembolso.',
        'en': 'Credit follow-up for enterprises: team, products, market, finances and repayment.',
        'id': 'Pendampingan kredit untuk perusahaan: tim, produk, pasar, keuangan, dan pembayaran.'},
    'prog_dnim_name': {'tet': 'Manufatureira', 'pt': 'Indústria Transformadora', 'en': 'Manufacturing', 'id': 'Manufaktur'},
    'prog_dnim': {
        'tet': 'Apoiu ba grupu indústria manufatureira: lokalizasaun, membru no atividade tinan-tinan.',
        'pt': 'Apoio a grupos da indústria transformadora: localização, membros e atividades anuais.',
        'en': 'Support to manufacturing groups: location, members and yearly activities.',
        'id': 'Dukungan untuk kelompok industri manufaktur: lokasi, anggota, dan kegiatan tahunan.'},
    'prog_mpms': {
        'tet': 'Rejistu empreza: lisensiamentu, kapitál, empregadór, matéria-prima no atividade.',
        'pt': 'Registo de empresas: licenciamento, capital, empregadores, matéria-prima e atividades.',
        'en': 'Enterprise registry: licensing, capital, employers, raw materials and activities.',
        'id': 'Registrasi perusahaan: perizinan, modal, pemberi kerja, bahan baku, dan kegiatan.'},

    'stats_title': {'tet': 'Estatístika benefisiáriu', 'pt': 'Estatísticas de beneficiários',
                    'en': 'Beneficiary statistics', 'id': 'Statistik penerima manfaat'},
    'stats_lead': {
        'tet': 'Númeru agregadu de\'it — la hatudu dadus pesoál.',
        'pt': 'Apenas números agregados — sem dados pessoais.',
        'en': 'Aggregated numbers only — no personal data is shown.',
        'id': 'Hanya angka agregat — tidak menampilkan data pribadi.'},
    'year_label': {'tet': 'Tinan', 'pt': 'Ano', 'en': 'Year', 'id': 'Tahun'},
    'all_years': {'tet': 'Tinan hotu', 'pt': 'Todos os anos', 'en': 'All years', 'id': 'Semua tahun'},
    'map_title': {'tet': 'Benefisiáriu tuir munisípiu', 'pt': 'Beneficiários por município',
                  'en': 'Beneficiaries by municipality', 'id': 'Penerima manfaat per munisipiu'},
    'map_hint': {'tet': 'Hili munisípiu iha mapa ka tabela.', 'pt': 'Selecione um município no mapa ou na tabela.',
                 'en': 'Select a municipality on the map or in the table.', 'id': 'Pilih munisipiu di peta atau tabel.'},
    'municipality': {'tet': 'Munisípiu', 'pt': 'Município', 'en': 'Municipality', 'id': 'Munisipiu'},
    'beneficiaries': {'tet': 'Benefisiáriu', 'pt': 'Beneficiários', 'en': 'Beneficiaries', 'id': 'Penerima manfaat'},
    'total': {'tet': 'Totál', 'pt': 'Total', 'en': 'Total', 'id': 'Total'},
    'fewer': {'tet': 'Menus', 'pt': 'Menos', 'en': 'Fewer', 'id': 'Sedikit'},
    'more': {'tet': 'Barak', 'pt': 'Mais', 'en': 'More', 'id': 'Banyak'},
    'no_location': {'tet': 'Lokalizasaun seidauk rejista', 'pt': 'Localização não registada',
                    'en': 'Location not recorded', 'id': 'Lokasi belum tercatat'},
    'no_data': {'tet': 'La iha dadus ba tinan ne\'e.', 'pt': 'Sem dados para este ano.',
                'en': 'No data for this year.', 'id': 'Tidak ada data untuk tahun ini.'},
    'load_error': {'tet': 'La konsege karrega estatístika. Koko fali.', 'pt': 'Não foi possível carregar as estatísticas. Tente novamente.',
                   'en': 'Statistics could not be loaded. Please try again.', 'id': 'Statistik gagal dimuat. Coba lagi.'},
    'chart_year': {'tet': 'Benefisiáriu tuir tinan', 'pt': 'Beneficiários por ano',
                   'en': 'Beneficiaries by year', 'id': 'Penerima manfaat per tahun'},
    'chart_program': {'tet': 'Benefisiáriu tuir programa', 'pt': 'Beneficiários por programa',
                      'en': 'Beneficiaries by programme', 'id': 'Penerima manfaat per program'},
    'chart_sex': {'tet': 'Benefisiáriu tuir seksu', 'pt': 'Beneficiários por sexo',
                  'en': 'Beneficiaries by sex', 'id': 'Penerima manfaat per jenis kelamin'},
    'male': {'tet': 'Mane', 'pt': 'Homens', 'en': 'Men', 'id': 'Laki-laki'},
    'female': {'tet': 'Feto', 'pt': 'Mulheres', 'en': 'Women', 'id': 'Perempuan'},
    'unknown': {'tet': 'La rejista', 'pt': 'Não registado', 'en': 'Not recorded', 'id': 'Tidak tercatat'},
    'download_csv': {'tet': 'Download dadus (CSV)', 'pt': 'Descarregar dados (CSV)',
                     'en': 'Download data (CSV)', 'id': 'Unduh data (CSV)'},
    'updated': {'tet': 'Atualiza', 'pt': 'Atualizado', 'en': 'Updated', 'id': 'Diperbarui'},
    'map_attr': {'tet': 'Limite munisípiu', 'pt': 'Limites municipais', 'en': 'Municipal boundaries', 'id': 'Batas munisipiu'},

    'info_title': {'tet': 'Informasaun importante', 'pt': 'Informação importante',
                   'en': 'Important information', 'id': 'Informasi penting'},
    'important': {'tet': 'Importante', 'pt': 'Importante', 'en': 'Important', 'id': 'Penting'},
    'notice_pw_title': {'tet': 'Proteje ita-boot nia konta', 'pt': 'Proteja a sua conta',
                        'en': 'Protect your account', 'id': 'Lindungi akun Anda'},
    'notice_pw': {
        'tet': 'MCI nunka husu password liuhusi telefone, SMS ka email. Troka password temporáriu iha login dahuluk.',
        'pt': 'O MCI nunca pede a palavra-passe por telefone, SMS ou email. Altere a palavra-passe temporária no primeiro acesso.',
        'en': 'MCI never asks for your password by phone, SMS or email. Change your temporary password at first sign-in.',
        'id': 'MCI tidak pernah meminta kata sandi lewat telepon, SMS, atau email. Ganti kata sandi sementara saat pertama masuk.'},
    'notice_benef_title': {'tet': 'Ba benefisiáriu', 'pt': 'Para beneficiários', 'en': 'For beneficiaries', 'id': 'Untuk penerima manfaat'},
    'notice_benef': {
        'tet': 'Benefisiáriu ho konta bele tama atu haree programa, hatama fluxu osan no haruka pedidu ka reklamasaun.',
        'pt': 'Os beneficiários com conta podem entrar para ver os seus programas, registar o fluxo de caixa e enviar pedidos ou reclamações.',
        'en': 'Beneficiaries with an account can sign in to see their programmes, record cash flow and send requests or complaints.',
        'id': 'Penerima manfaat yang punya akun dapat masuk untuk melihat program, mencatat arus kas, dan mengirim permintaan atau keluhan.'},
    'notice_data_title': {'tet': 'Kona-ba dadus', 'pt': 'Sobre os dados', 'en': 'About the data', 'id': 'Tentang data'},
    'notice_data': {
        'tet': 'Estatístika iha pajina ne\'e mai husi rejistu iha sistema no bele muda bainhira dadus foun tama.',
        'pt': 'As estatísticas desta página provêm dos registos do sistema e podem mudar à medida que entram novos dados.',
        'en': 'Statistics on this page come from system records and may change as new data is entered.',
        'id': 'Statistik di halaman ini berasal dari catatan sistem dan dapat berubah saat data baru masuk.'},

    'features_title': {'tet': 'Funsionalidade sistema', 'pt': 'Funcionalidades do sistema',
                       'en': 'System features', 'id': 'Fitur sistem'},
    'feat_offline_t': {'tet': 'Rejistu offline', 'pt': 'Registo offline', 'en': 'Offline registration', 'id': 'Pendaftaran offline'},
    'feat_offline': {
        'tet': 'Ofisiál rejista benefisiáriu iha kampu maski la iha internet, ho pozisaun GPS.',
        'pt': 'Os oficiais registam beneficiários no terreno sem internet, com posição GPS.',
        'en': 'Officers register beneficiaries in the field without internet, with GPS position.',
        'id': 'Petugas mendaftarkan penerima manfaat di lapangan tanpa internet, dengan posisi GPS.'},
    'feat_secure_t': {'tet': 'Seguransa konta', 'pt': 'Segurança da conta', 'en': 'Account security', 'id': 'Keamanan akun'},
    'feat_secure': {
        'tet': 'Verifikasaun pasu-2, blokeiu tentativa login sala no password temporáriu ne\'ebé tenke troka.',
        'pt': 'Verificação em dois passos, bloqueio de tentativas falhadas e palavra-passe temporária de troca obrigatória.',
        'en': 'Two-step verification, lockout after failed attempts and temporary passwords that must be changed.',
        'id': 'Verifikasi dua langkah, pemblokiran percobaan login gagal, dan kata sandi sementara yang wajib diganti.'},
    'feat_audit_t': {'tet': 'Auditoria', 'pt': 'Auditoria', 'en': 'Audit trail', 'id': 'Jejak audit'},
    'feat_audit': {
        'tet': 'Kada alterasaun dadus rejista ho utilizador, data no valór uluk no foun.',
        'pt': 'Cada alteração de dados é registada com utilizador, data e valores anterior e novo.',
        'en': 'Every data change is recorded with user, date and the old and new values.',
        'id': 'Setiap perubahan data dicatat beserta pengguna, tanggal, serta nilai lama dan baru.'},
    'feat_monitor_t': {'tet': 'Monitorizasaun', 'pt': 'Monitorização', 'en': 'Monitoring', 'id': 'Pemantauan'},
    'feat_monitor': {
        'tet': 'Baseline, monitorizasaun impaktu, fluxu osan no utilizasaun fundus ba kada negósiu.',
        'pt': 'Linha de base, monitorização de impacto, fluxo de caixa e utilização de fundos por negócio.',
        'en': 'Baseline, impact monitoring, cash flow and use of funds for each business.',
        'id': 'Baseline, pemantauan dampak, arus kas, dan penggunaan dana untuk setiap usaha.'},
    'feat_report_t': {'tet': 'Relatóriu no mapa', 'pt': 'Relatórios e mapas', 'en': 'Reports and maps', 'id': 'Laporan dan peta'},
    'feat_report': {
        'tet': 'Painel gráfiku, mapa lokalizasaun negósiu no esporta ba Excel no PDF.',
        'pt': 'Painéis gráficos, mapa de localização dos negócios e exportação para Excel e PDF.',
        'en': 'Chart dashboards, business location maps and export to Excel and PDF.',
        'id': 'Dasbor grafik, peta lokasi usaha, serta ekspor ke Excel dan PDF.'},
    'feat_lang_t': {'tet': 'Lian haat', 'pt': 'Quatro idiomas', 'en': 'Four languages', 'id': 'Empat bahasa'},
    'feat_lang': {
        'tet': 'Pajina públiku iha Tetun, Portugés, Inglés no Indonézia.',
        'pt': 'Página pública em tétum, português, inglês e indonésio.',
        'en': 'Public page in Tetum, Portuguese, English and Indonesian.',
        'id': 'Halaman publik dalam bahasa Tetun, Portugis, Inggris, dan Indonesia.'},

    'faq_title': {'tet': 'Pergunta ne\'ebé husu beibeik', 'pt': 'Perguntas frequentes',
                  'en': 'Frequently asked questions', 'id': 'Pertanyaan yang sering diajukan'},
    'q1': {'tet': 'Sé mak bele tama sistema?', 'pt': 'Quem pode entrar no sistema?',
           'en': 'Who can sign in to the system?', 'id': 'Siapa yang bisa masuk ke sistem?'},
    'a1': {
        'tet': 'Funsionáriu MCI ne\'ebé iha konta, no benefisiáriu ne\'ebé simu konta husi ofisiál programa.',
        'pt': 'Funcionários do MCI com conta e beneficiários que receberam uma conta do oficial do programa.',
        'en': 'MCI staff with an account, and beneficiaries who received an account from a programme officer.',
        'id': 'Pegawai MCI yang memiliki akun, dan penerima manfaat yang menerima akun dari petugas program.'},
    'q2': {'tet': 'Ha\'u haluha password. Halo saida?', 'pt': 'Esqueci-me da palavra-passe. O que faço?',
           'en': 'I forgot my password. What should I do?', 'id': 'Saya lupa kata sandi. Apa yang harus dilakukan?'},
    'a2': {
        'tet': 'Uza "Haluha password" iha pajina login, ka kontaktu ofisiál programa atu reset. Password foun temporáriu no tenke troka.',
        'pt': 'Use "Esqueci-me da palavra-passe" na página de entrada ou contacte o oficial do programa. A nova palavra-passe é temporária e tem de ser alterada.',
        'en': 'Use "Forgot password" on the sign-in page, or contact your programme officer for a reset. The new password is temporary and must be changed.',
        'id': 'Gunakan "Lupa kata sandi" di halaman masuk, atau hubungi petugas program untuk reset. Kata sandi baru bersifat sementara dan wajib diganti.'},
    'q3': {'tet': 'Estatístika ne\'e hatudu dadus pesoál ka lae?', 'pt': 'As estatísticas mostram dados pessoais?',
           'en': 'Do the statistics show personal data?', 'id': 'Apakah statistik menampilkan data pribadi?'},
    'a3': {
        'tet': 'Lae. Pajina públiku hatudu de\'it totál tuir munisípiu, tinan, programa no seksu.',
        'pt': 'Não. A página pública mostra apenas totais por município, ano, programa e sexo.',
        'en': 'No. The public page only shows totals by municipality, year, programme and sex.',
        'id': 'Tidak. Halaman publik hanya menampilkan total per munisipiu, tahun, program, dan jenis kelamin.'},
    'q4': {'tet': 'Bele uza iha telemovel ka lae?', 'pt': 'Posso usar no telemóvel?',
           'en': 'Can I use it on a phone?', 'id': 'Bisakah dipakai di ponsel?'},
    'a4': {
        'tet': 'Bele. Pajina ne\'e adapta ba ekran ki\'ik, no ofisiál bele instala rejistu offline hanesan aplikasaun.',
        'pt': 'Sim. A página adapta-se a ecrãs pequenos e os oficiais podem instalar o registo offline como aplicação.',
        'en': 'Yes. The page adapts to small screens, and officers can install offline registration as an app.',
        'id': 'Bisa. Halaman menyesuaikan layar kecil, dan petugas dapat memasang pendaftaran offline sebagai aplikasi.'},

    'contact_title': {'tet': 'Kontaktu', 'pt': 'Contacto', 'en': 'Contact', 'id': 'Kontak'},
    'address': {'tet': 'Enderesu', 'pt': 'Morada', 'en': 'Address', 'id': 'Alamat'},
    'phone': {'tet': 'Telefone', 'pt': 'Telefone', 'en': 'Phone', 'id': 'Telepon'},
    'email': {'tet': 'Email', 'pt': 'Email', 'en': 'Email', 'id': 'Email'},
    'rights': {'tet': 'Direitu hotu rezerva.', 'pt': 'Todos os direitos reservados.',
               'en': 'All rights reserved.', 'id': 'Hak cipta dilindungi.'},
    'back_top': {'tet': 'Fila ba leten', 'pt': 'Voltar ao topo', 'en': 'Back to top', 'id': 'Kembali ke atas'},
}


def strings(lang):
    """Fó fali dicionáriu tradusaun ba lian ida (fallback ba Tetun)."""
    return {key: values.get(lang) or values[DEFAULT] for key, values in _T.items()}


def all_keys_complete():
    return [key for key, values in _T.items() if set(values) != set(CODES)]
