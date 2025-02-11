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

  balancing.cpp --

  Original Author: Rocco Jonack, Synopsys, Inc., 1999-07-22

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "balancing.h"

void balancing::entry()
{

    sc_biguint<4> tmp1;
    sc_biguint<4> tmp2;
    sc_biguint<4> tmp3;
    sc_unsigned out_tmp2(12);
    sc_unsigned out_tmp3(12);

    // reset_loop
    if (reset.read() == true)
    {
        out_value1.write(0);
        out_value2.write(0);
        out_value3.write(0);
        out_valid1.write(false);
        out_valid2.write(false);
        out_valid3.write(false);
        wait();
    }
    else
        wait();

    //
    // main loop
    //
    while (1)
    {
        do
        {
            wait();
        } while (in_valid == false);

        // reading inputs
        tmp1 = in_value1.read();

        // easy, just a bunch of different waits
        out_valid1.write(true);
        if (tmp1 == 4)
        {
            wait();
            wait();
            wait();
            wait();
            out_value1.write(3);
            wait();
        }
        else if (tmp1 == 3)
        {
            out_value1.write(2);
            wait();
            wait();
            wait();
        }
        else if (tmp1 == 2)
        {
            out_value1.write(1);
            wait();
            wait();
        }
        else
        {
            out_value1.write(tmp1);
            wait();
        };
        out_valid1.write(false);
        wait();

        // the first branch should be pushed out in latency due to long delay
        tmp2 = in_value2.read();
        out_valid2.write(true);
        wait();
        if (tmp2 < 4)
        {
            // long operation should extent latency
            out_tmp2 = tmp2 * tmp2 * tmp2;
            wait();
        }
        else if (tmp2 < 8)
        {
            // short operation should not extent latency
            out_tmp2 = 4;
            wait();
        }
        else if (tmp2 < 12)
        {
            // wait statements should extent latency
            out_tmp2 = 1;
            wait();
            wait();
            wait();
        };
        wait();

        out_value2.write(sc_biguint<4>(out_tmp2));
        out_valid2.write(false);
        wait();

        // if branch without else
        tmp3 = in_value3.read();
        out_valid3.write(true);
        wait();
        if (tmp3 < 8)
        {
            out_tmp3 = 4;
            wait();
        }

        out_value3.write(sc_biguint<4>(out_tmp3));
        wait();
        out_valid3.write(false);
    }
}

// EOF
