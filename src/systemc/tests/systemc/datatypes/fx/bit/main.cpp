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

// This may look like C code, but it is really -*- C++ -*-
//
// main.cxx<3> --
// Copyright Synopsys 1998
// Author          : Ric Hilderink
// Created On      : Mon Jan 11 13:25:23 1999
// Status          : none
//

#define SC_INCLUDE_FX
#include "systemc.h"
#include "test_all.hh"

extern void test_bit(ostream &, int, int);

static void test_cases(ostream &out, int wl, int iwl)
{
    test_bit(out, wl, iwl);
}

int sc_main(int, char **)
{
    int wl = 0, iwl = 0;
    test_cases(cout, wl, wl);

    return 0;
}
