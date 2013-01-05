import sys
import alsaaudio

def init_pcm(pcm):
    pcm.setchannels(1)
    pcm.setrate(44100)
    pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    pcm.setperiodsize(160)

def play_music(src_fname=None, dst_fname=None):
    if src_fname is not None:
        print 'playing: ' + src_fname
        src_fr = open(src_fname, 'r')
    else:
        print 'now play your guitar!'
        inputt = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)
        init_pcm(inputt)

    if dst_fname is not None:
        print 'recording: ' + dst_fname
        dst_fw = open(dst_fname, 'w')

    output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    init_pcm(output)

    while True:
        if src_fname is not None:
            data = src_fr.read(160)
            if data == '':
                break
            l = True
        else:
            l, data = inputt.read()
        if l:
            output.write(data)
            if dst_fname is not None:
                dst_fw.write(data)
    print 'finished'

def watch_histogram(src_fname):
    print 'watch histogram of ' + src_fname

def play_file(src_fname):
    print 'play ' + src_fname

def print_usage():
    print 'usage:'
    print '    . playing the guitar on the fly'
    print '        python main.py'
    print '    . recording the guitar sound'
    print '        python main.py -o filename.jj'
    print '    . playing the guitar sound'
    print '        python main.py -i filename.jj'
    print '    . watching the histogram'
    print '        python main.py -i filename.jj -h'
    exit()

def main(argv):
    src_fname = None
    dst_fname = None
    histogram = False
    idx = 1
    while idx < len(argv):
        if argv[idx] == '-i':
            if idx >= len(argv) - 1:
                print_usage()
            src_fname = argv[idx + 1]
            idx += 1
        elif argv[idx] == '-o':
            if idx >= len(argv) - 1:
                print_usage()
            dst_fname = argv[idx + 1]
            idx += 1
        elif argv[idx] == '-h':
            histogram = True
        else:
            print_usage()
        idx += 1

    if src_fname != None and dst_fname == None:
        if histogram:
            watch_histogram(src_fname)
        else:
            play_music(src_fname=src_fname)
    elif src_fname == None and dst_fname != None and not histogram:
        play_music(dst_fname=dst_fname)
    elif src_fname == None and dst_fname == None and not histogram:
        play_music()
    else:
        print_usage()

if __name__ == '__main__':
    main(sys.argv)

