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

  main.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

/* Main file for pipeline simulation */

#include "display.h"
#include "numgen.h"
#include "testbench.h"
#include "f_pipeline.h"

int sc_main(int ac, char *av[])
{
    sc_signal<double> in1;
    sc_signal<double> in2;
    sc_signal<double> powr;

    in1 = 0.0;
    in2 = 0.0;
    powr = 0.0;

    sc_clock clk("CLOCK", 20.0, SC_NS, 0.5, 0.0, SC_NS);

    testbench T("Testbench", clk, powr, in1, in2);
    f_pipeline("PIPE", clk, in1, in2, powr);

    sc_start(1000, SC_NS);
    return 0;
}
