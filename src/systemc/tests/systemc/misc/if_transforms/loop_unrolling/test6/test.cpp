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

  test.cpp --

  Original Author: Martin Janssen, Synopsys, Inc., 2002-02-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

//
//	Verifies loop unrolling
//
//      Test Plan: 5.2
//      From 41.sc
//
//	Author: PRP
//	Date Created: 05 APR 99
//

#include "test.h"

void test::entry()
{
    int i, j, k, m;
    int a[10];

    a[0] = a[1] = i1;
    a[2] = a[3] = i2;
    a[4] = a[5] = i3;
    a[6] = a[7] = i4;
    a[8] = a[9] = i5;

    wait();

    for (i = 0; i < 2; i++)
        for (j = 0; j < 3; j++)
            for (k = 0; k < 4; k++)
                a[i] = 5;

    for (i = 0; i < 2; i++)
        for (j = 0; j < 3; j++)
            for (k = 0; k < 4; k++)
                for (m = 0; m < 2; m++)
                    a[i] = 6;

    o1 = a[0];
    o2 = a[2];
    o3 = a[4];
    o4 = a[6];
    o5 = a[8];

    wait();
}
