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

  modulo.cpp --

  Original Author: Rocco Jonack, Synopsys, Inc., 1999-05-13

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "modulo.h"

void modulo::entry()
{

    int tmp1;
    sc_bigint<4> tmp2;
    sc_biguint<4> tmp3;
    sc_bigint<8> tmp4;
    sc_biguint<8> tmp5;

    // reset_loop
    if (reset.read() == true)
    {
        out_valid.write(false);
        wait();
    }
    else
        wait();

    //
    // main loop
    //
    //
    while (1)
    {
        while (in_valid.read() == false)
            wait();
        wait();

        // reading the inputs
        tmp1 = in_value1.read();
        tmp2 = in_value2.read();
        tmp3 = in_value3.read();
        tmp4 = in_value4.read();
        tmp5 = in_value5.read();

        // execute operations
        tmp1 = tmp1 % 5;
        tmp2 = tmp2 % 5;
        tmp3 = tmp3 % 5;
        tmp4 = tmp4 % 5;
        tmp5 = tmp5 % 5;
        wait();

        // write outputs
        out_value1.write(tmp1);
        out_value2.write(tmp2);
        out_value3.write(tmp3);
        out_value4.write(tmp4);
        out_value5.write(tmp5);
        out_valid.write(true);
        wait();
        out_valid.write(false);
        wait();
        // execute self assignment operations
        tmp1 %= 3;
        tmp2 %= 3;
        tmp3 %= 3;
        tmp4 %= 3;
        tmp5 %= 3;
        wait();

        // write outputs
        out_value1.write(tmp1);
        out_value2.write(tmp2);
        out_value3.write(tmp3);
        out_value4.write(tmp4);
        out_value5.write(tmp5);
        out_valid.write(true);
        wait();
        out_valid.write(false);
        wait();
        // execute different type operations
        if (tmp3 != 0)
            tmp1 = (tmp2 % tmp3).to_int();
        if (tmp4 != 0)
            tmp2 = tmp2 % tmp4;
        if (tmp5 != 0)
            tmp3 = tmp3 % tmp5;
        if (tmp5 != 0)
            tmp4 = tmp4 % tmp5;
        wait();

        // write outputs
        out_value1.write(tmp1);
        out_value2.write(tmp2);
        out_value3.write(tmp3);
        out_value4.write(tmp4);
        out_value5.write(tmp5);
        out_valid.write(true);
        wait();
        out_valid.write(false);
        wait();
    }
}

// EOF
