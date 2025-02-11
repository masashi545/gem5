/*
    tests/test_custom_type_casters.cpp -- tests type_caster<T>

    Copyright (c) 2016 Wenzel Jakob <wenzel.jakob@epfl.ch>

    All rights reserved. Use of this source code is governed by a
    BSD-style license that can be found in the LICENSE file.
*/

#include "constructor_stats.h"
#include "pybind11_tests.h"

// py::arg/py::arg_v testing: these arguments just record their argument when invoked
class ArgInspector1 {
public:
    std::string arg = "(default arg inspector 1)";
};
class ArgInspector2 {
public:
    std::string arg = "(default arg inspector 2)";
};
class ArgAlwaysConverts {};
namespace pybind11 {
namespace detail {
template <>
struct type_caster<ArgInspector1> {
public:
    PYBIND11_TYPE_CASTER(ArgInspector1, _("ArgInspector1"));

    bool load(handle src, bool convert) {
        value.arg = "loading ArgInspector1 argument " + std::string(convert ? "WITH" : "WITHOUT")
                    + " conversion allowed.  "
                      "Argument value = "
                    + (std::string) str(src);
        return true;
    }

    static handle cast(const ArgInspector1 &src, return_value_policy, handle) {
        return str(src.arg).release();
    }
};
template <>
struct type_caster<ArgInspector2> {
public:
    PYBIND11_TYPE_CASTER(ArgInspector2, _("ArgInspector2"));

    bool load(handle src, bool convert) {
        value.arg = "loading ArgInspector2 argument " + std::string(convert ? "WITH" : "WITHOUT")
                    + " conversion allowed.  "
                      "Argument value = "
                    + (std::string) str(src);
        return true;
    }

    static handle cast(const ArgInspector2 &src, return_value_policy, handle) {
        return str(src.arg).release();
    }
};
template <>
struct type_caster<ArgAlwaysConverts> {
public:
    PYBIND11_TYPE_CASTER(ArgAlwaysConverts, _("ArgAlwaysConverts"));

    bool load(handle, bool convert) { return convert; }

    static handle cast(const ArgAlwaysConverts &, return_value_policy, handle) {
        return py::none().release();
    }
};
} // namespace detail
} // namespace pybind11

// test_custom_caster_destruction
class DestructionTester {
public:
    DestructionTester() { print_default_created(this); }
    ~DestructionTester() { print_destroyed(this); }
    DestructionTester(const DestructionTester &) { print_copy_created(this); }
    DestructionTester(DestructionTester &&) noexcept { print_move_created(this); }
    DestructionTester &operator=(const DestructionTester &) {
        print_copy_assigned(this);
        return *this;
    }
    DestructionTester &operator=(DestructionTester &&) noexcept {
        print_move_assigned(this);
        return *this;
    }
};
namespace pybind11 {
namespace detail {
template <>
struct type_caster<DestructionTester> {
    PYBIND11_TYPE_CASTER(DestructionTester, _("DestructionTester"));
    bool load(handle, bool) { return true; }

    static handle cast(const DestructionTester &, return_value_policy, handle) {
        return py::bool_(true).release();
    }
};
} // namespace detail
} // namespace pybind11

TEST_SUBMODULE(custom_type_casters, m) {
    // test_custom_type_casters

    // test_noconvert_args
    //
    // Test converting.  The ArgAlwaysConverts is just there to make the first no-conversion pass
    // fail so that our call always ends up happening via the second dispatch (the one that allows
    // some conversion).
    class ArgInspector {
    public:
        ArgInspector1 f(ArgInspector1 a, ArgAlwaysConverts) { return a; }
        std::string g(const ArgInspector1 &a,
                      const ArgInspector1 &b,
                      int c,
                      ArgInspector2 *d,
                      ArgAlwaysConverts) {
            return a.arg + "\n" + b.arg + "\n" + std::to_string(c) + "\n" + d->arg;
        }
        static ArgInspector2 h(ArgInspector2 a, ArgAlwaysConverts) { return a; }
    };
    // [workaround(intel)] ICC 20/21 breaks with py::arg().stuff, using py::arg{}.stuff works.
    py::class_<ArgInspector>(m, "ArgInspector")
        .def(py::init<>())
        .def("f", &ArgInspector::f, py::arg(), py::arg() = ArgAlwaysConverts())
        .def("g",
             &ArgInspector::g,
             "a"_a.noconvert(),
             "b"_a,
             "c"_a.noconvert() = 13,
             "d"_a             = ArgInspector2(),
             py::arg()         = ArgAlwaysConverts())
        .def_static("h", &ArgInspector::h, py::arg{}.noconvert(), py::arg() = ArgAlwaysConverts());
    m.def(
        "arg_inspect_func",
        [](const ArgInspector2 &a, const ArgInspector1 &b, ArgAlwaysConverts) {
            return a.arg + "\n" + b.arg;
        },
        py::arg{}.noconvert(false),
        py::arg_v(nullptr, ArgInspector1()).noconvert(true),
        py::arg() = ArgAlwaysConverts());

    m.def(
        "floats_preferred", [](double f) { return 0.5 * f; }, "f"_a);
    m.def(
        "floats_only", [](double f) { return 0.5 * f; }, "f"_a.noconvert());
    m.def(
        "ints_preferred", [](int i) { return i / 2; }, "i"_a);
    m.def(
        "ints_only", [](int i) { return i / 2; }, "i"_a.noconvert());

    // test_custom_caster_destruction
    // Test that `take_ownership` works on types with a custom type caster when given a pointer

    // default policy: don't take ownership:
    m.def("custom_caster_no_destroy", []() {
        static auto *dt = new DestructionTester();
        return dt;
    });

    m.def(
        "custom_caster_destroy",
        []() { return new DestructionTester(); },
        py::return_value_policy::take_ownership); // Takes ownership: destroy when finished
    m.def(
        "custom_caster_destroy_const",
        []() -> const DestructionTester * { return new DestructionTester(); },
        py::return_value_policy::take_ownership); // Likewise (const doesn't inhibit destruction)
    m.def("destruction_tester_cstats",
          &ConstructorStats::get<DestructionTester>,
          py::return_value_policy::reference);
}
