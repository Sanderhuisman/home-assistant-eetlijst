# Eetlijst Sensor <a name="eetlijst"></a>

An Eetlijst sensor to monitor the eat/cook status of your student home.

## Configuration

To use `eetlijst` in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: eetlijst
    username: !secret eetlijst_username
    password: !secret eetlijst_password
```

### Configuration variables

| Parameter             | Type                    | Description   |
| --------------------- | ----------------------- | ------------- |
| username              | string       (Required) | Username      |
| password              | string       (Required) | Password      |
