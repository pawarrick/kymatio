import pytest
import numpy as np

from kymatio.scattering1d.backend.tensorflow_backend import backend


def test_subsample_fourier(random_state=42):
    rng = np.random.RandomState(random_state)
    J = 10
    # 1d signal 
    x = rng.randn(2, 2**J) + 1j * rng.randn(2, 2**J)
    x_f = np.fft.fft(x, axis=-1)

    for j in range(J + 1):
        x_f_sub = backend.subsample_fourier(x_f, 2**j)
        x_sub = np.fft.ifft(x_f_sub, axis=-1)
        assert np.allclose(x[:, ::2**j], x_sub)

    with pytest.raises(TypeError) as te:
        x_bad = x.real
        backend.subsample_fourier(x_bad, 1)
    assert "should be complex" in te.value.args[0]

def test_pad():
    N = 128
    x = np.random.rand(2, 4, N)
    
    for pad_left in range(0, N - 16, 16):
        for pad_right in [pad_left, pad_left + 16]:
            x_pad = backend.pad(x, pad_left, pad_right)
            
            # compare left reflected part of padded array with left side 
            # of original array
            for t in range(1, pad_left + 1):
                assert np.allclose(x_pad[..., pad_left - t], x[..., t])
            # compare left part of padded array with left side of 
            # original array
            for t in range(x.shape[-1]):
                assert np.allclose(x_pad[..., pad_left + t], x[..., t])
            # compare right reflected part of padded array with right side
            # of original array
            for t in range(1, pad_right + 1):
                assert np.allclose(x_pad[..., x_pad.shape[-1] - 1 - pad_right + t], x[..., x.shape[-1] - 1 - t])
            # compare right part of padded array with right side of 
            # original array
            for t in range(1, pad_right + 1):
                assert np.allclose(x_pad[..., x_pad.shape[-1] - 1 - pad_right - t], x[..., x.shape[-1] - 1 - t])

    with pytest.raises(ValueError):
        backend.pad(x, x.shape[-1], 0)

    with pytest.raises(ValueError):
        backend.pad(x, 0, x.shape[-1])

