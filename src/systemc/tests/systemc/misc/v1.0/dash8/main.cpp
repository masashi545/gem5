/*****************************************************************************

  Licensed to Accellera Systems Initiative Inc. (Accellera) under one or
  more contributor license agreements.  See the NOTICE file distributed
  with this work for additional information regarding copyright ownership.
  Accellera licenses this file to you under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with the
  License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
  implied.  See the License for the specific language governing
  permissions and limitations under the License.

 *****************************************************************************/

/*****************************************************************************

  main.cpp -- Main function for the dashboard controller for a
           car. This controller contains a speedometer, two odometers (total
           and partial distance), the driver of the car, clocks, and the
           pulse generator. The pulses are generated by the sensors placed
           around one of the wheel shafts. The rate of pulse generation is
           determined by the speed of the car. The driver can start the car,
           set its speed, reset the partial distance odometer, and stop the
           car (which means he will stop the simulation). One of the clocks
           is slow and the other is fast. The fast clock represents the real
           time. The slow clock is used to control the actions of the
           driver. The signals in this program are traced.

           purpose (in terms of changes to dash7's purpose) -- Positional
           connection method for binding the ports of modules. Example: Let m
           be a module with ports p1 and p2. Let m_ptr be a pointer to m, and
           let p1_arg and p2_arg be the ports that we want to bind to p1 and
           p2 of m. Then, we can do the binding in one of the following:

           m(p1_arg, p2_arg);  or (*m_ptr)(p1_arg, p2_arg);
           m.p1(p1_arg); m.p2.bind(p2_arg); or
           m_ptr->p1(p1_arg); m->p2.bind(p2_arg);

           The output of this program is identical to that of dash6 and dash7.

  Original Author: Ali Dasdan, Synopsys, Inc.

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

// $Log: main.cpp,v $
// Revision 1.2  2011/01/07 01:20:20  acg
//  Andy Goodrich: update for new IEEE 1666.
//
// Revision 1.1.1.1  2006/12/15 20:26:24  acg
// systemc_tests-2.3
//
// Revision 1.5  2006/01/24 21:05:58  acg
//  Andy Goodrich: replacement of deprecated features with their non-deprecated
//  counterparts.
//
// Revision 1.4  2006/01/20 00:43:24  acg
// Andy Goodrich: Changed over to use putenv() instead of setenv() to accommodate old versions of Solaris.
//
// Revision 1.3  2006/01/19 00:48:20  acg
// Andy Goodrich: Changes for the fact signal write checking is enabled.
//
// Revision 1.2  2006/01/18 00:23:51  acg
// Change over from SC_NO_WRITE_CHECK to sc_write_check_enable() call.
//

#define SC_NO_WRITE_CHECK
#include "systemc.h"
#include "const.h"
#include "driver.h"
#include "pulse.h"
#include "speed.h"
#include "dist.h"

int sc_main(int argc, char *argv[])
{
    // Pulses for the speedometer and odometers, generated by the pulse
    // generator.
    sc_signal<bool> speed_pulses("speed_pulses");
    sc_signal<bool> dist_pulses("dist_pulses");
    // Signals for the driver's actions.
    sc_signal<bool> reset("reset");
    sc_signal<int> speed("speed");
    sc_signal<bool> start("start");

    // Signals observed by the driver.
    sc_signal<double> disp_speed("disp_speed");
    sc_signal<double> disp_angle("disp_angle");
    sc_signal<double> disp_total_dist("disp_total_dist");
    sc_signal<double> disp_partial_dist("disp_partial_dist");

    // Clocks.
    sc_clock clk0("slow_clk", SLOW_CLOCK_PERIOD0, SC_NS, 0.5, 0.0, SC_NS, true);
    sc_clock clk1("fast_clk", FAST_CLOCK_PERIOD1, SC_NS, 0.5, 0.0, SC_NS, false);

    driver_mod driver("driver");
    driver(clk0, disp_speed, disp_angle, disp_total_dist,
           disp_partial_dist, reset, speed, start);

    gen_pulse_mod gen_pulse("gen_pulse");
    gen_pulse(clk1, start, speed, speed_pulses, dist_pulses);

    speed_mod speedometer("speedometer");
    speedometer(clk1, start, speed_pulses, disp_speed, disp_angle);

    dist_mod odometers("odometers");
    odometers.pulse(dist_pulses);
    odometers.reset(reset);
    odometers.start.bind(start);
    odometers.total(disp_total_dist);
    odometers.partial.bind(disp_partial_dist);

    // Initialize signals:
    start = false;

    // Tracing:
    // Trace file creation.
    sc_trace_file *tf = sc_create_vcd_trace_file("dash");
    // External signals.
    sc_trace(tf, clk0, "slow_clk");
    sc_trace(tf, clk1, "fast_clk");
    sc_trace(tf, speed_pulses, "speed_pulses");
    sc_trace(tf, dist_pulses, "dist_pulses");
    sc_trace(tf, reset, "reset");
    sc_trace(tf, start, "start");
    sc_trace(tf, speed, "speed");
    sc_trace(tf, disp_speed, "disp_speed");
    sc_trace(tf, disp_angle, "disp_angle");
    sc_trace(tf, disp_total_dist, "disp_total_dist");
    sc_trace(tf, disp_partial_dist, "disp_partial_dist");
    // Internal signals.
    sc_trace(tf, speedometer.elapsed_time, "elapsed_time");
    sc_trace(tf, speedometer.read_mod->raw_speed, "raw_speed");
    sc_trace(tf, speedometer.filtered_speed, "filtered_speed");
    sc_trace(tf, odometers.ok_for_incr, "ok_for_incr");
    sc_trace(tf, odometers.total_dist, "total_dist");
    sc_trace(tf, odometers.partial_dist, "partial_dist");

    disp_speed = 0.0;
    disp_angle = 0.0;
    disp_total_dist = 0.0;
    disp_partial_dist = 0.0;

    sc_start();

    return 0;
}

// End of file
