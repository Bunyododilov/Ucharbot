import yt_dlp

def download_video(url, format="mp4"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "video")
        ext = info.get("ext", "mp4")
        filename = f"downloads/{title}.{ext}"
        ydl.download([url])
        return filename, title
