"""
Recording/STFT.py
envmixer

2012 Brandon Mechtley
Arizona State University
http://plantseeds.me/

Simple functions to compute the Short-Time Fourier Transform and its inverse.
"""

import numpy as np
from scipy import fftpack as fp

def ISTFT(x, nhop=512, trunc=0, progress=None):
    """
    Reconstruct a one-dimensional signal from an STFT matrix.
    
    Args:
        x (numpy.ndarray): the STFT to convert back to a signal
        nhop (int): distance between frames in samples (default 512)
        trunc (int): number of samples to which to truncate the output if > 0 (default 0).
        progress (progressbar.ProgressBar): optional progress bar for debug output (default None).
    
    Returns:
        Reconstructed one-channel waveform as numpy.ndarray.
    """
    
    frames, nfft = x.shape
    wav = np.zeros(frames * nhop + nfft)
    
    if progress: 
        progress.maxval = len(x)
        progress.start()
    
    for i, frame in enumerate(x):
        wav[i * nhop:i * nhop + nfft] += np.real(fp.ifft(frame))
        
        if progress:
            progress.update(i + 1)
    
    if trunc:
        wav = wav[:trunc]
    
    if progress:
        progress.finish()
    
    return wav

def STFT(signal, nfft=1024, nhop=512, winfun=np.hanning, progress=None):
    """
    Return an STFT matrix for a one-dimensional waveform.
    
    Args:
        signal (numpy.ndarray): the signal to transform
        nfft (int): size of the analysis window in samples (default 1024).
        nhop (int): distance between frames in samples (default 512)
    
    Returns:
        Two-dimensional numpy.ndarray where each row is a frame of FFT bins.
    """
    
    n = int(np.ceil(len(signal) / float(nhop)))
    window = winfun(nfft)
    
    # Zero-pad last frame.
    signal = np.concatenate((signal, np.zeros(n * nhop + (nfft - nhop) - len(signal))))
    
    # Create a matrix of hopped signal frames and take their FFT.
    if progress:
        progress.maxval = n
        progress.start()
    
    stft = np.zeros((n, nfft), dtype=np.complex64)
    for i in range(n):
        offset = i * nhop
        frame = signal[offset:offset + nfft]
        stft[i] = np.fft.fft(frame * window)
        
        if progress:
            progress.update(i + 1)
    
    if progress:
        progress.finish()
    
    return stft
