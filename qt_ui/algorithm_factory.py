from __future__ import annotations  # multiple return values
import numpy as np

from device.focstim.fourphase_algorithm import FOCStimFourphaseAlgorithm
from device.neostim.algorithm import NeoStimAlgorithm
from device.coyote.algorithm import CoyoteAlgorithm
from qt_ui.device_wizard.enums import DeviceConfiguration, DeviceType, WaveformType
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from device.focstim.algorithm import FOCStimAlgorithm
from stim_math.audio_gen.pulse_based import DefaultThreePhasePulseBasedAlgorithm, ABTestThreePhasePulseBasedAlgorithm
from stim_math.audio_gen.continuous import ThreePhaseAlgorithm
from stim_math.audio_gen.params import *

from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.models.script_mapping import ScriptMappingModel
from qt_ui.device_wizard.axes import AxisEnum
from stim_math.axis import create_precomputed_axis, AbstractTimestampMapper, create_constant_axis, AbstractMediaSync


class AlgorithmFactory:
    def __init__(self, mainwindow,
                 kit: FunscriptKitModel,
                 script_mapping: ScriptMappingModel,
                 timestamp_mapper: AbstractTimestampMapper,
                 media_sync: AbstractMediaSync,
                 load_funscripts: bool = True,
                 create_for_bake: bool = False,
                 ):
        # TODO: not very nice to reference mainwindow...
        self.mainwindow = mainwindow
        self.kit = kit
        self.script_mapping = script_mapping
        self.timestamp_mapper = timestamp_mapper
        self.media_sync = media_sync
        self.load_funscripts = load_funscripts
        self.create_for_bake = create_for_bake

    def create_algorithm(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm | NeoStimAlgorithm | CoyoteAlgorithm:
        if device.device_type == DeviceType.AUDIO_THREE_PHASE:
            if device.waveform_type == WaveformType.CONTINUOUS:
                return self.create_3phase_continuous(device)
            elif device.waveform_type == WaveformType.PULSE_BASED:
                return self.create_3phase_pulsebased(device)
            elif device.waveform_type == WaveformType.A_B_TESTING:
                return self.create_3phase_abtest(device)
            else:
                raise RuntimeError('unknown waveform type')
        elif device.device_type == DeviceType.FOCSTIM_THREE_PHASE:
            return self.create_focstim_3phase_pulsebased(device)
        elif device.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            return self.create_focstim_4phase_pulsebased(device)
        elif device.device_type == DeviceType.NEOSTIM_THREE_PHASE:
            return self.create_neostim(device)
        elif device.device_type == DeviceType.COYOTE_THREE_PHASE:
            return self.create_coyote(device)
        else:
            raise RuntimeError('unknown device type')

    def create_3phase_continuous(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = ThreePhaseAlgorithm(
            self.media_sync,
            ThreephaseContinuousAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_continuous_carrier_frequency(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_3phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = DefaultThreePhasePulseBasedAlgorithm(
            self.media_sync,
            ThreephasePulsebasedAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_3phase_abtest(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = ABTestThreePhasePulseBasedAlgorithm(
            self.media_sync,
            ThreephaseABTestAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                a_volume=self.mainwindow.tab_a_b_testing.axis_a_volume,
                a_train_duration=self.mainwindow.tab_a_b_testing.axis_a_train_duration,
                a_carrier_frequency=self.mainwindow.tab_a_b_testing.axis_a_carrier_frequency,
                a_pulse_frequency=self.mainwindow.tab_a_b_testing.axis_a_pulse_frequency,
                a_pulse_width=self.mainwindow.tab_a_b_testing.axis_a_pulse_width,
                a_pulse_interval_random=self.mainwindow.tab_a_b_testing.axis_a_pulse_interval_random,
                a_pulse_rise_time=self.mainwindow.tab_a_b_testing.axis_a_pulse_rise_time,
                b_volume=self.mainwindow.tab_a_b_testing.axis_b_volume,
                b_train_duration=self.mainwindow.tab_a_b_testing.axis_b_train_duration,
                b_carrier_frequency=self.mainwindow.tab_a_b_testing.axis_b_carrier_frequency,
                b_pulse_frequency=self.mainwindow.tab_a_b_testing.axis_b_pulse_frequency,
                b_pulse_width=self.mainwindow.tab_a_b_testing.axis_b_pulse_width,
                b_pulse_interval_random=self.mainwindow.tab_a_b_testing.axis_b_pulse_interval_random,
                b_pulse_rise_time=self.mainwindow.tab_a_b_testing.axis_b_pulse_rise_time,
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            ),
            waveform_change_callback=self.mainwindow.tab_a_b_testing.test_waveform_changed,
        )
        return algorithm

    def create_focstim_3phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FOCStimAlgorithm(
            self.media_sync,
            FOCStimParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
                tau=self.get_axis_tau(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_focstim_4phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FOCStimFourphaseAlgorithm(
            self.media_sync,
            FourphaseFOCStimParams(
                position=FourphasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                    self.get_axis_gamma(),
                ),
                # transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_fourphase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
                tau=self.get_axis_tau(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_neostim(self, device: DeviceConfiguration) -> NeoStimAlgorithm:
        algorithm = NeoStimAlgorithm(
            self.media_sync,
            NeoStimParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                voltage=self.get_axis_neostim_voltage(),
                pulse_frequency=self.get_axis_neostim_pulse_frequency(),
                duty_cycle_at_max_power=self.get_axis_neostim_duty_cycle_at_max_power(),
                carrier_frequency=self.get_axis_neostim_carrier_frequency(),
                inversion_time=self.get_axis_neostim_inversion_time(),
                switch_time=self.get_axis_neostim_switch_time(),
                debug=self.get_axis_neostim_debug(),
            ),
        )
        return algorithm
    
    def create_coyote(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        """
        Create direct algorithm for Coyote device with proper frequency handling.

        Each channel can take:
        - Vibration axis if available (assumed already in reasonable range or scaled directly).
        - Pulse frequency (1-100 mapped directly into channel's range).
        - Carrier frequency (global, used if pulse frequency is missing).
        - Fallback to constant 100 if none exist.

        Pulse width and rise time are **always required** by the algorithm, so fallbacks are handled here.
        """

        # Fetch frequency axes
        carrier_frequency = self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY, limits=(0, 100))
        pulse_frequency = self.get_axis_from_script_mapping(AxisEnum.PULSE_FREQUENCY, limits=(0, 100))
        fallback_frequency = create_constant_axis(100)

        # Fetch pulse shape axes (always needed, so provide defaults: 100% width, rise: 0%)
        # pulse_width = self.get_axis_from_script_mapping(AxisEnum.PULSE_WIDTH, limits=(0, 100)) or create_constant_axis(100)
        # pulse_rise_time = self.get_axis_from_script_mapping(AxisEnum.PULSE_RISE_TIME, limits=(0, 100)) or create_constant_axis(0)

        # Vibration axes (optional, not yet used)
        # vibration_1 = self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_FREQUENCY)  # Consider for Channel A effects?
        # vibration_2 = self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_FREQUENCY)  # Consider for Channel B effects?

        # Prefer pulse frequency → fallback to carrier frequency → fallback to constant 100
        script_frequency = pulse_frequency or carrier_frequency or create_constant_axis(100)

        # Get frequency limits from kit
        carrier_freq_limits = self.kit.limits_for_axis(AxisEnum.CARRIER_FREQUENCY)
        pulse_freq_limits = self.kit.limits_for_axis(AxisEnum.PULSE_FREQUENCY)

        # Create the algorithm
        algorithm = CoyoteAlgorithm(
            self.media_sync,
            CoyoteAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
                channel_a=CoyoteChannelParams(
                    minimum_frequency=settings.coyote_channel_a_freq_min,
                    maximum_frequency=settings.coyote_channel_a_freq_max,
                    maximum_strength=settings.coyote_channel_a_strength_max,
                    vibration=self.get_axis_vib1_all()
                ),
                channel_b=CoyoteChannelParams(
                    minimum_frequency=settings.coyote_channel_b_freq_min,
                    maximum_frequency=settings.coyote_channel_b_freq_max,
                    maximum_strength=settings.coyote_channel_b_strength_max,
                    vibration=self.get_axis_vib2_all()
                )
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            ),
            carrier_freq_limits=carrier_freq_limits,
            pulse_freq_limits=pulse_freq_limits
        )
        return algorithm

    def get_axis_alpha(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_ALPHA) or self.mainwindow.alpha

    def get_axis_beta(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_BETA) or self.mainwindow.beta

    def get_axis_gamma(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_GAMMA) or self.mainwindow.gamma

    def get_axis_volume_api(self):
        return self.get_axis_from_script_mapping(AxisEnum.VOLUME_API) or self.mainwindow.tab_volume.axis_api_volume

    def get_axis_volume_master(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # ramp does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_master_volume

    def get_axis_volume_inactivity(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # inactivity does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_inactivity_volume

    def get_axis_volume_external(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # external volume does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_external_volume

    def get_axis_tau(self):
        return self.mainwindow.tab_volume.axis_tau

    def get_axis_continuous_carrier_frequency(self):
        default = self.mainwindow.tab_carrier.axis_carrier
        return self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY) or default

    def get_axis_pulse_carrier_frequency(self):
        default = self.mainwindow.tab_pulse_settings.axis_carrier_frequency
        return self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY) or default

    def get_axis_pulse_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_FREQUENCY) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_frequency

    def get_axis_pulse_width(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_WIDTH) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_width

    def get_axis_pulse_interval_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_INTERVAL_RANDOM) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_interval_random

    def get_axis_pulse_rise_time(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_RISE_TIME) or \
            self.mainwindow.tab_pulse_settings.axis_pulse_rise_time

    def get_axis_vib1_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib1_enabled(),
            frequency=self.get_axis_vib1_frequency(),
            strength=self.get_axis_vib1_strength(),
            left_right_bias=self.get_axis_vib1_left_right_bias(),
            high_low_bias=self.get_axis_vib1_high_low_bias(),
            random=self.get_axis_vib1_random(),
        )

    def get_axis_vib1_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_1.enabled

    def get_axis_vib1_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_1.frequency

    def get_axis_vib1_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_1.strength

    def get_axis_vib1_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.left_right_bias

    def get_axis_vib1_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.high_low_bias

    def get_axis_vib1_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_1.random

    def get_axis_vib2_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib2_enabled(),
            frequency=self.get_axis_vib2_frequency(),
            strength=self.get_axis_vib2_strength(),
            left_right_bias=self.get_axis_vib2_left_right_bias(),
            high_low_bias=self.get_axis_vib2_high_low_bias(),
            random=self.get_axis_vib2_random(),
        )

    def get_axis_vib2_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_2.enabled

    def get_axis_vib2_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_2.frequency

    def get_axis_vib2_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_2.strength

    def get_axis_vib2_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.left_right_bias

    def get_axis_vib2_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.high_low_bias

    def get_axis_vib2_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_2.random

    def get_axis_neostim_voltage(self):
        return self.mainwindow.tab_neostim.axis_voltage

    def get_axis_neostim_carrier_frequency(self):
        return self.mainwindow.tab_neostim.axis_carrier_frequency

    def get_axis_neostim_pulse_frequency(self):
        return self.mainwindow.tab_neostim.axis_pulse_frequency

    def get_axis_neostim_duty_cycle_at_max_power(self):
        return self.mainwindow.tab_neostim.axis_duty_cycle_at_max_power

    def get_axis_neostim_inversion_time(self):
        return self.mainwindow.tab_neostim.axis_inversion_time

    def get_axis_neostim_switch_time(self):
        return self.mainwindow.tab_neostim.axis_switch_time

    def get_axis_neostim_debug(self):
        return self.mainwindow.tab_neostim.axis_debug

    def get_axis_from_script_mapping(self, axis: AxisEnum, limits: Optional[(int, int)] = None) -> AbstractAxis | None:
        if not self.load_funscripts:
            return None

        funscript_item = self.script_mapping.get_config_for_axis(axis)
        if funscript_item:
            limit_min, limit_max = limits or self.kit.limits_for_axis(axis)
            # TODO: not very memory efficient if multiple algorithms reference the same script.
            # but worst-case it only wastes a few MB or so...
            return create_precomputed_axis(funscript_item.script.x,
                                           np.clip(funscript_item.script.y, 0, 1) * (limit_max - limit_min) + limit_min,
                                           self.timestamp_mapper)
        else:
            return None
