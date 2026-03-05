import yt_dlp
import os


def baixar(url, tipo):
    """
    Função responsável por configurar e executar o download.
    Recebe:
    - url: link do YouTube
    - tipo: '1' para vídeo / '2' para áudio
    """

    # 🔹 Cria a pasta Downloads caso ela não exista
    if not os.path.exists('Downloads'):
        os.makedirs('Downloads')

    # 🔹 Configurações base do yt_dlp
    opcoes = {
        # Define nome e pasta do arquivo
        'outtmpl': 'Downloads/%(title)s.%(ext)s',
        # Permitimos playlist inicialmente (vamos tratar depois)
        'noplaylist': False,
        'progress_hooks': [progresso],  # Função para mostrar progresso
        'ignoreerrors': False,  # Para o download se ocorrer erro
    }

    # 🔹 Se o usuário escolheu VÍDEO
    if tipo == '1':
        opcoes['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        print("\n🎬 Modo selecionado: VÍDEO (MP4)")

    # 🔹 Se o usuário escolheu ÁUDIO
    else:
        opcoes['format'] = 'bestaudio/best'
        opcoes['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',   # Usa ffmpeg para converter
            'preferredcodec': 'mp3',       # Converte para MP3
            'preferredquality': '192',     # Qualidade 192kbps
        }]
        print("\n🎵 Modo selecionado: ÁUDIO (MP3)")

    try:
        # 🔹 Inicializa o yt_dlp com as opções definidas
        with yt_dlp.YoutubeDL(opcoes) as ydl:

            # 🔹 Extrai informações do link sem baixar ainda
            info = ydl.extract_info(url, download=False)

            # 🔹 Verifica se é playlist
            if 'entries' in info:
                print(
                    f"\n📂 Detectada playlist com {len(info['entries'])} vídeos.")

                escolha_playlist = input(
                    "Deseja baixar:\n"
                    "1 - Apenas o primeiro vídeo\n"
                    "2 - Todos os vídeos\n"
                    "Escolha: "
                )

                # 🔹 Se escolher apenas 1 vídeo
                if escolha_playlist == '1':
                    primeiro_video = info['entries'][0]['webpage_url']
                    ydl.download([primeiro_video])

                # 🔹 Se escolher todos
                elif escolha_playlist == '2':
                    ydl.download([url])

                else:
                    print("Opção inválida.")
                    return
            else:
                # 🔹 Se for vídeo único
                ydl.download([url])

        print("\n✅ Download concluído com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro durante o download: {e}")


def progresso(d):
    """
    Função chamada automaticamente durante o download.
    Mostra progresso em tempo real.
    """
    if d['status'] == 'downloading':
        print(f"⏳ Baixando... {d['_percent_str']} ", end='\r')

    elif d['status'] == 'finished':
        print("\n🔄 Processando arquivo...")


if __name__ == "__main__":
    print("=== DOWNLOADER PRO MAX (MP4/MP3) ===")

    # 🔹 Solicita URL ao usuário
    url = input("Cole o link do YouTube: ").strip()

    # 🔹 Menu de escolha do formato
    print("\nComo deseja baixar?")
    print("1 - Vídeo (MP4)")
    print("2 - Áudio (MP3)")
    escolha = input("Digite 1 ou 2: ")

    # 🔹 Validação básica
    if url and escolha in ['1', '2']:
        baixar(url, escolha)
    else:
        print("❌ URL ou opção inválida.")
