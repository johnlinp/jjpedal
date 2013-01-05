import sys
import time
import alsaaudio, audioop
from matplotlib import pyplot

PCM_RATE = 44100
PCM_PERIOD_SIZE = 160
PCM_FORMAT = alsaaudio.PCM_FORMAT_S16_LE
READ_BUF_LENGTH = 200

def init_pcm(pcm):
    pcm.setchannels(1)
    pcm.setrate(PCM_RATE)
    pcm.setformat(PCM_FORMAT)
    pcm.setperiodsize(PCM_PERIOD_SIZE)

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
            data = src_fr.read(PCM_PERIOD_SIZE)
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

def sample_to_int(sample):
    assert PCM_FORMAT == alsaaudio.PCM_FORMAT_S16_LE
    byte0 = ord(sample[0])
    byte1 = ord(sample[1])
    num = (byte0 | (byte1 << 8)) & 0x7FFF
    negative = (byte0 | (byte1 << 8)) & 0x8000
    if negative:
        return num - 0x8000
    else:
        return num

def raw_to_list(data):
    assert PCM_FORMAT == alsaaudio.PCM_FORMAT_S16_LE
    res = []
    width = 2
    num_samples = len(data) / width
    for idx in range(num_samples):
        datum = data[idx * width : (idx + 1) * width]
        num = sample_to_int(datum)
        assert num == audioop.getsample(data, width, idx)
        res.append(num)
    return res

def watch_histogram(src_fname):
    print 'watch histogram of ' + src_fname
    src_fr = open(src_fname, 'r')

    output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    init_pcm(output)

    pyplot.ion()
    pyplot.ylabel('Amplification')
    pyplot.xlabel('Time')
    pyplot.axhline(color='black')
    pyplot.ylim(-4096, 4096)
    lines = pyplot.plot([0], 'blue')
    while True:
        data = src_fr.read(READ_BUF_LENGTH * PCM_PERIOD_SIZE)
        if len(data) < READ_BUF_LENGTH * PCM_PERIOD_SIZE:
            break

        lines[0].remove()
        lines = pyplot.plot(raw_to_list(data), 'blue')
        pyplot.draw()

        idx = 0
        while idx < READ_BUF_LENGTH * PCM_PERIOD_SIZE:
            output.write(data[idx : idx + PCM_PERIOD_SIZE])
            idx += PCM_PERIOD_SIZE
    print 'finished'

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

