import wave
import numpy as np

class AudioEnergyDetector:
    def __init__(self, frame_duration_ms=100):
        self.frame_duration_ms = frame_duration_ms

    def analyze_audio_energy(self, wav_path: str) -> list:
        """
        Analyzes 16kHz mono WAV audio to calculate RMS energy, local relative surge,
        and scream/laughter spikes across time windows.
        Returns a list of dicts: [{'time': float_sec, 'energy': float_norm_0_to_1, 'is_spike': bool, 'surge_factor': float}]
        """
        with wave.open(wav_path, "rb") as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            num_frames = wf.getnframes()
            audio_bytes = wf.readframes(num_frames)

        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        if num_channels > 1:
            samples = samples.reshape(-1, num_channels).mean(axis=1)

        # Normalize samples to 0..1 peak
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples /= max_val

        window_size = int(sample_rate * (self.frame_duration_ms / 1000.0))
        num_windows = len(samples) // window_size

        timeline = []
        rms_values = []

        for i in range(num_windows):
            start = i * window_size
            end = start + window_size
            chunk = samples[start:end]
            rms = float(np.sqrt(np.mean(chunk**2)))
            rms_values.append(rms)
            timeline.append((i * (self.frame_duration_ms / 1000.0), rms))

        if not rms_values:
            return []

        rms_arr = np.array(rms_values)
        mean_rms = float(np.mean(rms_arr))
        std_rms = float(np.std(rms_arr))
        global_spike_thresh = mean_rms + (1.2 * std_rms)

        # 5-second rolling baseline for detecting sudden bursts (screams, laughter, hype yells)
        half_window = int(2.5 / (self.frame_duration_ms / 1000.0)) # 25 frames = 2.5s
        results = []

        for idx, (t, val) in enumerate(timeline):
            w_start = max(0, idx - half_window)
            w_end = min(len(rms_arr), idx + half_window + 1)
            local_baseline = float(np.mean(rms_arr[w_start:w_end])) or 0.001
            surge_factor = val / local_baseline

            # A spike is a sudden scream/gasp/laugh that is both loud globally and significantly above local talk
            is_spike = bool((val > global_spike_thresh or surge_factor > 2.2) and val > 0.10)

            results.append({
                "time": round(t, 2),
                "energy": float(val),
                "is_spike": is_spike,
                "surge_factor": round(surge_factor, 2)
            })

        return results

    def get_hype_score_for_range(self, energy_timeline: list, start_time: float, end_time: float) -> float:
        """
        Calculates a calibrated hype score (0.0 to 100.0) for a given time window,
        measuring vocal energy intensity, scream peaks, and reaction density.
        """
        segment_items = [
            item for item in energy_timeline
            if start_time <= item["time"] <= end_time
        ]
        if not segment_items:
            return 0.0

        energies = [it["energy"] for it in segment_items]
        spikes = [it for it in segment_items if it.get("is_spike")]

        avg_energy = float(np.mean(energies)) # usually 0.02 - 0.45
        peak_energy = float(np.max(energies)) # usually 0.10 - 1.00
        spike_count = len(spikes)             # count of hype reaction bursts
        duration_sec = max(1.0, end_time - start_time)
        spike_density = spike_count / duration_sec # spikes per second

        # Calibrated 0 to 100 score:
        # 1. Average vocal volume intensity (up to 35 pts)
        vol_score = min(35.0, (avg_energy / 0.25) * 35.0)
        # 2. Peak scream / laugh volume (up to 35 pts)
        peak_score = min(35.0, (peak_energy / 0.75) * 35.0)
        # 3. Burst / reaction density (up to 30 pts)
        density_score = min(30.0, (spike_density / 0.35) * 30.0)

        total_score = vol_score + peak_score + density_score
        return min(round(total_score, 1), 99.9)
