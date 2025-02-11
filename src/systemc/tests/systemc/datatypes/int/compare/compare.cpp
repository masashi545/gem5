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

  compare.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

#include "systemc.h"

int sc_main(int argc, char *argv[])
{
    sc_bigint<8> a, b;
    sc_biguint<8> c;

    a = -5;
    b = -1;
    c = -1;
    sc_assert(a <= b);
    sc_assert(a <= c);

    a = -5;
    b = 0;
    c = 0;
    sc_assert(a <= b);
    sc_assert(a <= c);

    a = -5;
    b = 5;
    c = 5;
    sc_assert(a <= b);
    sc_assert(a <= c);

    a = 0;
    b = 5;
    c = 5;
    sc_assert(a <= b);
    sc_assert(a <= c);

    a = 5;
    b = 10;
    c = 10;
    sc_assert(a <= b);
    sc_assert(a <= c);

    return 0;
}
