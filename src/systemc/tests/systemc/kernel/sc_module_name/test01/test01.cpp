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

  test01.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

// test of module inheritance and sc_module_name

#include "systemc.h"

class base_mod
    : public sc_module
{
public:
    base_mod(sc_module_name name_)
        : sc_module(name_)
    {
    }
};

class derived_mod
    : public base_mod
{
public:
    derived_mod(sc_module_name name_)
        : base_mod(name_)
    {
    }
};

int sc_main(int, char *[])
{
    base_mod m1("m1");
    derived_mod m2("m2");

    sc_start(0, SC_NS);

    cout << m1.name() << endl;
    cout << m2.name() << endl;

    return 0;
}
