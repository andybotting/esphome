#pragma once

#include "esphome/components/switch/switch.h"
#include "mitsubishi_uart.h"

namespace esphome {
namespace mitsubishi_itp {

class MUARTSwitch : public switch_::Switch, public Component, public Parented<MitsubishiUART> {
 public:
  MUARTSwitch() = default;
  using Parented<MitsubishiUART>::Parented;

 protected:
  void write_state(bool state) override = 0;
};

class Zone0Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(0, state)) {
      publish_state(state);
    }
  }
};

class Zone1Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(1, state)) {
      publish_state(state);
    }
  }
};

class Zone2Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(2, state)) {
      publish_state(state);
    }
  }
};

class Zone3Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(3, state)) {
      publish_state(state);
    }
  }
};

class Zone4Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(4, state)) {
      publish_state(state);
    }
  }
};

class Zone5Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(5, state)) {
      publish_state(state);
    }
  }
};

class Zone6Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(6, state)) {
      publish_state(state);
    }
  }
};

class Zone7Switch : public MUARTSwitch {
 protected:
  void write_state(bool state) {
    if (parent_->set_zone(7, state)) {
      publish_state(state);
    }
  }
};

}  // namespace mitsubishi_itp
}  // namespace esphome