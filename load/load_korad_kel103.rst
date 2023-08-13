.. SPDX-FileCopyrightText: 2023 Jérôme Carretero <cJ@zougloub.eu>
.. SPDX-License-Identifier: GFDL-1.3-only

###############################
KORAD KEL-103 Programmable Load
###############################


References
##########


The best reference is:
https://www.distrelec.biz/en/electronic-dc-load-programmable-120v-30a-300w-rnd-lab-rnd-320-kel103/p/30126024

with some documents that can't be found on KORAD's website (some
documents are a bit confused, and the device comes with a CD-ROM
with some proprietary software).

- https://media.distrelec.com/Web/Downloads/_t/ds/RND%20320-KEL103_eng_tds.pdf


- https://media.distrelec.com/Web/Downloads/_m/an/Communication%20Commands%20with%20Computer.pdf


- https://media.distrelec.com/Web/Downloads/_m/an/IP%20LAN%20Communication%20Protocol.pdf


- https://media.distrelec.com/Web/Downloads/_m/an/RND320-KEL102_eng_man.pdf

  Calibration procedure



Communication Protocol
######################


Communication Interfaces
************************

- Serial port - configuration is done on the instrument front panel
  (shfit+0 ; select between 57600 and "15200" for 115200.

  Uses SCPI with \n EOL for TX and RX.

- Ethernet uses SCPI-as-UDP.

  Factory configuration uses a non-DHCP configuration, which kind of
  sucks if you expect to use the Ethernet interface out of the box.


SCPI Commands
*************

.. list-table::

   * - Command
     - Description

   * - *IDN?
     -

   * - :SYST:DEVINFO?

     - Query some device info

       ::

          DHCP:1
          IP:192.168.1.198
          NETMASK:255.255.255.0
          GateWay:192.168.1.1
          MAC:ab-cd-00-00-ff-ff
          PORT:18190
          BAUDRATE:115200

   * - .. code:: scpi

          :SYST:IPADdress?
          :SYST:DHCP?
          :SYST:DHCP ON
          :SYST:MAC?
          :SYST:PORT?
          :SYSTem:SMASK?
          :SYSTem:GATEway?
     - Get/set network interface configuration

   * - .. code:: scpi

          :SYST: FACTRESET
          :SYST:BAUD?
          :STAT?

     -

   * - .. code:: scpi

          :SYST:BEEP?
          :SYST:BAUD?
          :STAT?

     - ``STAT?`` queries beep and baud rate at once, with other
       undertermined values. It is essentially useless unless proven otherwise.

   * - .. code:: scpi

          :FUNC?
          :FUNC CC
          :FUNC CV
          :FUNC CW
          :FUNC CR

     - Query function, set function

   * - .. code:: scpi

          :CURR?
          :CURR 0.01A
          :VOLT?
          :VOLT 1V
          :VOLT MIN
          :VOLT MAX
          :VOLT:LOWer?
          :VOLT:UPPer?
          :POW?
          :POW 1W
          :POW:LOWer?
          :RES?
          :RES 200OHM
          :RES:LOWer?

     - Get/set setpoint (when setting, it automatically switches to
       CC/CV/CW/CR function)

   * - .. code:: scpi

          :MEAS:CURR?
          :MEAS:VOLT?
          :MEAS:POW?

     - Measurement

   * - .. code:: scpi

          *SAV 2
          *RCL 1
          *RCL 2

     - Save/recall operating configuration

   * - .. code:: scpi

         :INP?
         :INP 1
         :INP 0

     - Enable/disable input (close or open circuit)

   * - .. code:: scpi

          ???

     - 6. short-curcuit function

   * - .. code:: scpi

          :DYN 1,1.25V,1.3V,0.1HZ,10%
          :DYN 2,1.5A/uS,1.2A/uS,0.1A,0.2A,0.5HZ,10.000%
          :DYN 5,0.01A/uS,0.02A/uS,0.1A,0.2A,3S
          :DYN 6,0.01A/uS,0.02A/uS,0.1A,0.2A
          :DYN?
          *TRG
          :INP 0

     - 7. dynamic test function

       Dynamic mode:

       - 1 is CV : enter 2 CV values, a cycle frequency and a duty cycle
         (ratio of last CV duration on first CV duration)
       - 2 is CC : set slow rates, current setpoints, and duty cycle
         (TODO what does the duty cycle contain?).
       - 3 is CR (syntax same as CV).
       - 4 is CW (syntax same as CV).
       - 5 is dynamic pulse : pulse of configurable width is
         triggered (TODO how exactly is the pulse width measured given
         there's a slope?).
       - 6 is dynamic toggle : set 2 current setpoints and a rate,
         and trigger will toggle between the two.

   * - .. code:: scpi

          :LIST 5,0.3A,2,0.1A,0.01A/uS,2S,0.2A,0.01A/uS,2S,3
          :RCL:LIST 5
          :RCL:LIST?
          *TRG

     - Sequential operation function

       Create list in slot 5, with 2 steps at current range 0.3 A,
       the first step reaches 0.1 A with 0.01 A/µs, dwells for 2
       seconds,
       the first step reaches 0.2 A with 0.01 A/µs, dwells for 2
       seconds,
       the list is repeated 3 times.

       Recall the list and display it.
       Trigger the list.

   * - .. code:: scpi

          :BATT 2,1A,0.5A,1.2V,1.1AH,1M
          :RCL:BATT?
          :BATT:TIM?
          :BATT:CAP?

     - 9. Battery test function

       The feature allows to measure a battery performance easily /
       autonomously.

       Create battery testing (CC) list in slot 2, current range 1 A,
       use a current of 0.5 A, cutoff voltage of 1.2 V,
       cutoff capacity 1.1AH, and cutoff discharge time 1 min.

       Obtain discharge time, and capacity.

   * - .. code:: scpi

          :OCP
          :RCL:OCP?

     - 10. OCP test function

       TODO

   * - .. code:: scpi

          :OPP
          :RCL:OPP?

     - 11. OPP test function

       TODO


   * - .. code:: scpi

          *TRG

     - 12. External trigger function

       Used to toggle between things, and cause pulses.

   * - .. code:: scpi

          :SYST:LOCK ON
          :SYST:LOCK OFF
          :SYST:LOCK?

     - Lock from local use

   * - .. code:: scpi

          :SYST:EXIT ON
          :SYST:EXIT OFF
          :SYST:EXIT?

     - TODO

   * - .. code:: scpi

          :SYST:COMP ON
          :SYST:COMP OFF
          :SYST:COMP?

     - 13. remote compensation function

       TODO
