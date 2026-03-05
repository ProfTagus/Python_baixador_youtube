import yt_dlp
import os
import sys

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
        # 🔹 IMPORTANTE: Impede o download de playlists automaticamente
        'noplaylist': True,  # Mudamos de False para True
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
            
            # 🔹 Primeiro, vamos extrair informações para verificar se é playlist
            print("\n🔍 Verificando link...")
            info = ydl.extract_info(url, download=False)
            
            # 🔹 Verifica se é playlist
            if 'entries' in info:
                print("\n" + "="*60)
                print("🚫 ** PLAYLIST DETECTADA ** 🚫")
                print("="*60)
                print(f"\n📂 Este link é uma PLAYLIST com {len(info['entries'])} vídeos.")
                print("\n⚠️  Este programa foi configurado para baixar APENAS VÍDEOS INDIVIDUAIS.")
                print("\n❌ Download INTERROMPIDO por segurança.")
                print("\n💡 Dica: Se você realmente deseja baixar a playlist,")
                print("   será necessário modificar o código ou usar outro programa.")
                print("\n" + "="*60)
                return  # Interrompe a execução da função
            
            # 🔹 Se não for playlist, prossegue com o download
            print("\n✅ Link válido! Iniciando download...")
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
        # Mostra o progresso de forma mais limpa
        percentual = d['_percent_str'].strip()
        velocidade = d.get('_speed_str', '?').strip()
        tamanho = d.get('_total_bytes_str', '?').strip()
        print(f"⏳ Baixando... {percentual} de {tamanho} | {velocidade}   ", end='\r')

    elif d['status'] == 'finished':
        print("\n🔄 Processando arquivo...")

if __name__ == "__main__":
    print("="*60)
    print("🎥 DOWNLOADER DE VÍDEOS INDIVIDUAIS (NÃO SUPORTA PLAYLISTS) 🎥")
    print("="*60)
    
    while True:
        # 🔹 Solicita URL ao usuário
        url = input("\n📎 Cole o link do YouTube (ou 'sair' para encerrar): ").strip()
        
        if url.lower() == 'sair':
            print("👋 Programa encerrado.")
            break
        
        if not url:
            print("❌ URL não pode estar vazia!")
            continue
        
        # 🔹 Menu de escolha do formato
        print("\n📦 Como deseja baixar?")
        print("1 - Vídeo (MP4)")
        print("2 - Áudio (MP3)")
        escolha = input("👉 Digite 1 ou 2: ").strip()

        # 🔹 Validação básica
        if escolha in ['1', '2']:
            baixar(url, escolha)
        else:
            print("❌ Opção inválida! Digite apenas 1 ou 2.")
        
        print("\n" + "-"*60)