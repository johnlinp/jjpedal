import alsaaudio

def init_pcm(pcm):
    pcm.setchannels(1)
    pcm.setrate(96000)
    pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    pcm.setperiodsize(160)

def main():
    inputt = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)
    output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)

    init_pcm(inputt)
    init_pcm(output)

    while True:
        l, data = inputt.read()
        if l:
            output.write(data)

if __name__ == '__main__':
    main()

