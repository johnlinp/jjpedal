import sys
import time
import alsaaudio, audioop
from matplotlib import pyplot
from numpy import fft
from scipy import signal
import numpy
import math

PCM_RATE = 44100
PCM_PERIOD_SIZE = 160
PCM_FORMAT = alsaaudio.PCM_FORMAT_S16_LE
READ_BUF_LENGTH = 200
DISTORTION_CUTOFF = 100
DISTORTION_MULTI = 5

def init_pcm(pcm):
    pcm.setchannels(1)
    pcm.setrate(PCM_RATE)
    pcm.setformat(PCM_FORMAT)
    pcm.setperiodsize(PCM_PERIOD_SIZE)

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

def int_to_sample(num):
    assert PCM_FORMAT == alsaaudio.PCM_FORMAT_S16_LE
    negative = num < 0
    if negative:
        num += 0x8000
    byte0 = num & 0x00FF
    byte1 = (num & 0xFF00) >> 8
    if negative:
        byte1 |= 0x80
    sample = chr(byte0) + chr(byte1)
    return sample

def raw_to_list(samples):
    assert PCM_FORMAT == alsaaudio.PCM_FORMAT_S16_LE
    res = []
    width = 2
    num_samples = len(samples) / width
    for idx in range(num_samples):
        sample = samples[idx * width : (idx + 1) * width]
        num = sample_to_int(sample)
        assert num == audioop.getsample(samples, width, idx)
        assert int_to_sample(num) == sample
        res.append(num)
    return res

def list_to_raw(numbers):
    assert PCM_FORMAT == alsaaudio.PCM_FORMAT_S16_LE
    res = ''
    for num in numbers:
        res += int_to_sample(num)
    return res

def distortion(samples):
    numbers = raw_to_list(samples)
    for idx, num in enumerate(numbers):
        if num > DISTORTION_CUTOFF:
            numbers[idx] = DISTORTION_CUTOFF
        elif num < -DISTORTION_CUTOFF:
            numbers[idx] = -DISTORTION_CUTOFF
        numbers[idx] *= DISTORTION_MULTI
    return list_to_raw(numbers)

alpha = [0.0]
prev_y = []
def wahwah(samples):
    numbers = raw_to_list(samples)

    delay = 10
    R = 0.9
    y = [0]*len(numbers)
    output = [0]*len(numbers)
    for n in range(0,len(numbers)):
        alpha[0]  += 0.0001
        fb = numpy.complex(math.cos(alpha[0]),math.sin(alpha[0]))
        if(n-delay<0):
            if len(prev_y) == 0:
                y[n] = numbers[n]*(1-fb)
            else:
                y[n] = prev_y[n-delay]*R*fb + numbers[n]*(1-fb)
        else:
            y[n] = y[n-delay]*R*fb + numbers[n]*(1-fb)
        output[n] = int(float(y[n].real))
    prev_y[:] = y[-delay:]
    return list_to_raw(output)

def play_music(src_fname=None, dst_fname=None, effects=None):
    if effects == None:
        effects = []
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
            samples = src_fr.read(PCM_PERIOD_SIZE)
            if samples == '':
                break
            length = True
        else:
            length, samples = inputt.read()
        if length:
            for eff in effects:
                samples = eff(samples)
            output.write(samples)
            if dst_fname is not None:
                dst_fw.write(samples)
    print 'finished'

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
        samples = src_fr.read(READ_BUF_LENGTH * PCM_PERIOD_SIZE)
        if len(samples) < READ_BUF_LENGTH * PCM_PERIOD_SIZE:
            break

        lines[0].remove()
        lines = pyplot.plot(raw_to_list(samples), 'blue')
        pyplot.draw()

        idx = 0
        while idx < READ_BUF_LENGTH * PCM_PERIOD_SIZE:
            output.write(samples[idx : idx + PCM_PERIOD_SIZE])
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
    print '    . add distortion effect'
    print '        python main.py -e distortion'
    exit()

def main(argv):
    src_fname = None
    dst_fname = None
    histogram = False
    effects = []
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
        elif argv[idx] == '-e':
            if idx >= len(argv) - 1:
                print_usage()
            if argv[idx + 1] == 'distortion':
                effects.append(distortion)
            elif argv[idx + 1] == 'wahwah':
                effects.append(wahwah)
            else:
                print_usage()
            idx += 1
        else:
            print_usage()
        idx += 1

    if src_fname != None and dst_fname == None:
        if histogram:
            watch_histogram(src_fname)
        else:
            play_music(src_fname=src_fname, effects=effects)
    elif src_fname == None and dst_fname != None and not histogram:
        play_music(dst_fname=dst_fname, effects=effects)
    elif src_fname == None and dst_fname == None and not histogram:
        play_music(effects=effects)
    elif src_fname != None and dst_fname != None and not histogram:
        play_music(src_fname=src_fname, dst_fname=dst_fname, effects=effects)
    else:
        print_usage()

if __name__ == '__main__':
    main(sys.argv)

