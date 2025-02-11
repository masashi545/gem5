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

  datatypes.cpp --

  Original Author: Rocco Jonack, Synopsys, Inc., 1999-07-14

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "datatypes.h"

void datatypes::entry()

{

    sc_bigint<8> tmp1;
    sc_bigint<8> tmp1r;
    sc_biguint<8> tmp2;
    sc_biguint<8> tmp2r;
    long tmp3;
    long tmp3r;
    int tmp4;
    int tmp4r;
    short tmp5;
    short tmp5r;
    char tmp6;
    char tmp6r;

    // define 1 dimensional array
    int tmp7[2];
    char tmp8[2];

    // reset_loop
    if (reset.read() == true)
    {
        out_valid.write(false);
        out_ack.write(false);
        wait();
    }
    else
        wait();

    //
    // main loop
    //

    // initialization of sc_array

    tmp7[0] = 3;
    tmp7[1] = 12;
    tmp8[0] = 'R';
    tmp8[1] = 'G';

    while (1)
    {
        while (in_valid.read() == false)
            wait();

        // reading the inputs
        tmp1 = in_value1.read();
        tmp2 = in_value2.read();
        tmp3 = in_value3.read();
        tmp4 = in_value4.read();
        tmp5 = in_value5.read();
        tmp6 = in_value6.read();

        out_ack.write(true);

        // execute mixed data type subtraction operations
        tmp1r = tmp1 - tmp2;
        tmp2r = tmp6 - tmp1;
        tmp3r = tmp4 - tmp6;
        tmp4r = --tmp5;
        tmp4r -= 1;
        tmp5r = tmp6 - tmp4;
        tmp6r = tmp8[0] - tmp7[1];

        // write outputs
        out_value1.write(tmp1r);
        out_value2.write(tmp2r);
        out_value3.write(tmp3r);
        out_value4.write(tmp4r);
        out_value5.write(tmp5r);
        out_value6.write(tmp6r);

        out_valid.write(true);
        wait();
        out_ack.write(false);
        out_valid.write(false);
    }

} // End
