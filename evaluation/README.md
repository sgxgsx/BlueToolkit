# BlueToolkit Evaluation

## Automotive Case Study

We tested 22 cars from the following manufacturers and were able to find 60+ new vulnerabilities in them:
Audi, BMW, Chevrolet, Honda, Hyundai, Mercedes-Benz, Mini, Opel, Polestar, Renault, Skoda, Toyota, VW, Tesla.

We responsibly disclosed all of the vulnerabilities. All manufacturers had time to fix the vulnerabilities but not all of them did or wanted to!

| Manufacturer  | Model           | Year | BT version | Vuln Type | Vulnerability                          | Status                                        | Comment                                                                                      |
|---------------|-----------------|------|------------|-----------|----------------------------------------|-----------------------------------------------|----------------------------------------------------------------------------------------------|
| Audi          | A5              | 2020 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Audi          | A5              | 2020 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Audi          | A5              | 2020 | 4,2        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| Audi          | E-tron          | 2020 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Audi          | E-tron          | 2020 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Audi          | E-tron          | 2020 | 4,2        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| BMW           | X2              | 2021 | 4          | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| BMW           | X2              | 2021 | 4          | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| BMW           | X2              | 2021 | 4          | Chaining  | SC not supported                       |                                               |                                                                                              |
| Chevrolet     | Corvette        | 2018 | 3          | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Chevrolet     | Corvette        | 2018 | 3          | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Chevrolet     | Corvette        | 2018 | 3          | Chaining  | SC not supported                       |                                               |                                                                                              |
| Honda         | e               | 2020 | 5          | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Honda         | e               | 2020 | 5          | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Honda         | e               | 2020 | 5          | Chaining  | Always Pairable                        |                                               |                                                                                              |
| Hyundai       | Kona            | 2022 | 5          | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Hyundai       | Kona            | 2022 | 5          | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Hyundai       | Kona            | 2022 | 5          | Chaining  | SC not supported                       |                                               |                                                                                              |
| Hyundai       | Kona            | 2022 | 5          | Chaining  | Always Pairable                        |                                               |                                                                                              |
| Mercedes-Benz | Sprinter 316CDI | 2021 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Mercedes-Benz | Sprinter 316CDI | 2021 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Mercedes-Benz | Sprinter 316CDI | 2021 | 4,2        | Chaining  | SC not supported                       |                                               |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | Chaining  | SC not supported                       |                                               |                                                                                              |
| Opel          | Astra           | 2019 | 4,1        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Opel          | Astra           | 2019 | 4,1        | Chaining  | SC not supported                       |                                               |                                                                                              |
| Polestar      | Polestar 2      | 2022 | 4,2        | Chaining  | SC not supported                       |                                               | Not fully tested!                                                                            |
| Renault       | Megane          | 2016 | 2,1        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | Chaining  | SC not supported                       |                                               |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | Chaining  | SC not supported                       |                                               |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | Chaining  | SC not supported                       |                                               |                                                                                              |
| Skoda         | Octavia         | 2015 | 3          | Chaining  | IVI is not rebootable                  |                                               | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2015 | 3          | Chaining  | SC not supported                       |                                               | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2019 | 3          | Chaining  | SC not supported                       |                                               | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2022 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| Skoda         | Octavia         | 2022 | 4,2        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| Toyota        | Corolla         | 2023 | 5,1        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| VW            | Caddy           | 2023 | 4,2        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| VW            | Caddy           | 2023 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| VW            | Caddy           | 2023 | 4,2        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| VW            | ID.3            | 2022 | 4,2        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| VW            | ID.3            | 2022 | 4,2        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | Chaining  | IVI is not rebootable                  |                                               |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | Chaining  | Not only IVI can initiate a connection |                                               |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | Chaining  | SC not supported                       |                                               |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | Chaining  | Always Pairable                        |                                               |                                                                                              |
| Opel          | Astra           | 2019 | 4,1        | Critical  | CVE-2018-19860                         | Fixed in new versions                         |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | Critical  | Contact extractor                      | Unknown                                       |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | Critical  | Contact extractor                      | Unknown                                       |                                                                                              |
| Skoda         | Octavia         | 2015 | 3          | Critical  | CVE-2018-19860                         | Acknowledged. Working on a fix                | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2015 | 3          | Critical  | Contact extractor                      | Acknowledged. Working on a fix                | Not fully tested!                                                                            |
| VW            | T6.1            | 2021 | 4,1        | Critical  | Contact extractor                      | Acknowledged. Working on a fix                |                                                                                              |
| Audi          | A5              | 2020 | 4,2        | DoS       | invalid_max_slot                       | Acknowledged. Working on a fix                | (probably known) (Broadcom - Cypress)                                                        |
| BMW           | X2              | 2021 | 4          | DoS       | au_rand_flooding                       | Acknowledged. Fixed in new hardware           |                                                                                              |
| BMW           | X2              | 2021 | 4          | DoS       | truncated_sco_request                  | Acknowledged. Fixed in new hardware           | (unknown) Texas Instruments                                                                  |
| BMW           | X2              | 2021 | 4          | DoS       | invalid_timing_accuracy                | Acknowledged. Fixed in new hardware           | (unknown) Texas Instruments                                                                  |
| Chevrolet     | Corvette        | 2018 | 3          | DoS       | lmp_overflow_2dh1                      | Unknown                                       | (unknown) (Qualcomm)                                                                         |
| Chevrolet     | Corvette        | 2018 | 3          | DoS       | invalid_timing_accuracy                | Unknown                                       | (known WCN3990) (Qualcomm)                                                                   |
| Mercedes-Benz | Sprinter 316CDI | 2021 | 4,2        | DoS       | invalid_max_slot                       | Unknown                                       | (unknown) Marvell Technology                                                                 |
| Mini          | Cooper S        | 2022 | 5          | DoS       | au_rand_flooding                       | Acknowledged. Fixed in new hardware           |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | DoS       | lmp_auto_rate_overflow                 | Acknowledged. Fixed in new hardware           | False positive probably - recovered after 40 seconds                                         |
| Opel          | Astra           | 2019 | 4,1        | DoS       | lmp_overflow_dm1                       | Acknowledged. But might be discarded?         | (unknown)  (chip problem Cypress)                                                            |
| Opel          | Astra           | 2019 | 4,1        | DoS       | invalid_timing_accuracy                | Acknowledged. But might be discarded?         | (unknown)  (chip problem Cypress)                                                            |
| Opel          | Astra           | 2019 | 4,1        | DoS       | truncated_lmp_accepted                 | Acknowledged. But might be discarded?         | (unknown)  (chip problem Cypress)                                                            |
| Polestar      | Polestar 2      | 2022 | 4,2        | DoS       | duplicated_encapsulated_payload        | Acknowledged. Had problems reproducing        | Not fully tested!  (unknown) (Qualcomm)                                                      |
| Renault       | Megane          | 2016 | 2,1        | DoS       | invalid_timing_accuracy                | Unknown                                       | Might be a false positive as this is the data from the first run !!!!!                       |
| Renault       | Megane          | 2021 | 4,2        | DoS       | au_rand_flooding                       | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | lmp_invalid_transport                  | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | lmp_max_slot_overflow                  | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | invalid_max_slot                       | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | truncated_sco_request                  | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | sdp_unknown_element                    | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | Megane          | 2021 | 4,2        | DoS       | duplicated_encapsulated_payload        | Unknown                                       | (unknown) (Marvell Technology)                                                               |
| Renault       | ZOE             | 2021 | 4,2        | DoS       | invalid_max_slot                       | Unknown                                       |                                                                                              |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | feature_req_ping_pong                  | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | wrong_encapsulated_payload             | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | duplicated_iocap                       | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | lmp_overflow_dm1                       | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | sdp_oversized_element_size             | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | duplicated_encapsulated_payload        | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | invalid_max_slot                       | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Toyota        | Corolla         | 2023 | 5,1        | DoS       | invalid_timing_accuracy                | Acknowledged                                  | Marvell technology chip has an actual vulnerability (unknown before)                         |
| Audi          | A5              | 2020 | 4,2        | MitM      | Insecure NC implementation             | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| Audi          | A5              | 2020 | 4,2        | MitM      | KNOB                                   | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| Audi          | E-tron          | 2020 | 4,2        | MitM      | Insecure NC implementation             | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| BMW           | X2              | 2021 | 4          | MitM      | NiNo                                   | Acknowledged. Working on a fix                |                                                                                              |
| BMW           | X2              | 2021 | 4          | MitM      | CVE-2018-5383                          | Acknowledged. Not fixing, fixed in new hardw. |                                                                                              |
| BMW           | X2              | 2021 | 4          | MitM      | Insecure NC implementation             | Acknowledged. Working on a fix                |                                                                                              |
| BMW           | X2              | 2021 | 4          | MitM      | E0 Algorithm is used (due to BT vers)  | Acknowledged. Working on a fix                |                                                                                              |
| Chevrolet     | Corvette        | 2018 | 3          | MitM      | KNOB                                   | Unknown                                       |                                                                                              |
| Chevrolet     | Corvette        | 2018 | 3          | MitM      | E0 Algorithm is used (due to BT vers)  | Unknown                                       |                                                                                              |
| Honda         | e               | 2020 | 5          | MitM      | NiNo                                   | Acknowledged                                  |                                                                                              |
| Honda         | e               | 2020 | 5          | MitM      | Insecure NC implementation             | Acknowledged                                  |                                                                                              |
| Honda         | e               | 2020 | 5          | MitM      | KNOB                                   | Acknowledged                                  |                                                                                              |
| Honda         | e               | 2020 | 5          | MitM      | Vehicular NiNo                         | Acknowledged                                  |                                                                                              |
| Hyundai       | Kona            | 2022 | 5          | MitM      | Insecure NC implementation             | Unknown                                       |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | MitM      | NiNo                                   | Acknowledged. Working on a fix                |                                                                                              |
| Mini          | Cooper S        | 2022 | 5          | MitM      | Insecure NC implementation             | Acknowledged. Working on a fix                |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | MitM      | NiNo                                   | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | MitM      | CVE-2018-5383                          | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | MitM      | KNOB                                   | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | MitM      | Legacy Pairing enabled                 | Unknown                                       | code 0000                                                                                    |
| Renault       | Megane          | 2016 | 2,1        | MitM      | E0 Algorithm is used (due to BT vers)  | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2016 | 2,1        | MitM      | SSP not supported                      | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | MitM      | Insecure NC implementation             | Unknown                                       |                                                                                              |
| Renault       | Megane          | 2021 | 4,2        | MitM      | Vehicular NiNo                         | Unknown                                       |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | MitM      | NiNo                                   | Unknown                                       | Might have been marked as vulnerable due to Vehicular NiNo (should be checked independently) |
| Renault       | ZOE             | 2021 | 4,2        | MitM      | Insecure NC implementation             | Unknown                                       |                                                                                              |
| Renault       | ZOE             | 2021 | 4,2        | MitM      | Vehicular NiNo                         | Unknown                                       |                                                                                              |
| Skoda         | Octavia         | 2015 | 3          | MitM      | KNOB                                   | Acknowledged.                                 | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2015 | 3          | MitM      | E0 Algorithm is used (due to BT vers)  | Acknowledged.                                 | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2019 | 3          | MitM      | KNOB                                   | Acknowledged.                                 | Not fully tested!                                                                            |
| Skoda         | Octavia         | 2019 | 3          | MitM      | E0 Algorithm is used (due to BT vers)  | Acknowledged.                                 | Not fully tested!                                                                            |
| Tesla         | Model Y         | 2023 | 5,2        | MitM      | Vehicular NiNo                         | Not fixing. Usability feature                 |                                                                                              |
| VW            | ID.3            | 2022 | 4,2        | MitM      | Vehicular NiNo                         | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | MitM      | KNOB                                   | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | MitM      | NiNo                                   | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | MitM      | Vehicular NiNo                         | Acknowledged. Fixing in a new firmw. version  |                                                                                              |
| VW            | T6.1            | 2021 | 4,1        | MitM      | CVE-2018-5383                          | Acknowledged. Fixing in a new firmw. version  |                                                                   

## Additional vulnerabilities discovered 
These vulnerabilities were discovered accidentally while using this framework or we are not sure about the results shown by the tool and human in the loop. Nevertheless the vulnerabilities were reported to the manufacturers.

| Manufacturer  | Model           | Year | BT version | Vuln Type | Vulnerability                          | Status                                        | Comment                                                                                      |
|---------------|-----------------|------|------------|-----------|----------------------------------------|-----------------------------------------------|----------------------------------------------------------------------------------------------|
| Renault       | Megane          | 2021 | 4,2        | MitM      | NiNo                                   | Unknown                                       | Might have been marked as vulnerable due to Vehicular NiNo (should be checked independently) |
| Tesla         | Model Y         | 2023 | 5,2        |           | Accidental crash (on BT connection)    | Not reproduced                                |          


## Novel Attacks

#### Insecure NC Implementation

The IVI system does not properly implement the Numeric Comparison authentication protocol as in the core specification of the Bluetooth which makes a link to be non-authenticated and thus vulnerable to the NiNo, Method Confusion and custom MitM attacks.

There are 3 possible variations:
1. The IVI/device doesn't require a confirmation for pairing (e.g. no button to confirm the pairing) (Renault, Hyundai cars)
2. The static number is always shown. (BMW, Mini cars)
3. The IVI shows a pairing window without a pairing number to compare. (Audi)

There are 2 possible reasons:
1. State problem
2. Design problem

In case of the state problem an adversary needs to connect to the IVI(other device) with a capability other than DisplayYesNo and the IVI should try to execute a broken Numeric Comparison and not Passkey or Just Works.

In case of a design problem, one simply needs to observe the pairing process and what is required of a used on a target device (IVI). 

Examples of vulnerable cars:
<img src="/static/exampleInsecureNC.png" alt="ExampleInsecureNC">
 
For the PoC steps please consult [contact extractor documentation](https://github.com/sgxgsx/BlueToolkit/wiki/Manual-Exploits)

#### Vehicular NiNo
The vehicle allows connections to a device with no input or output capabilities. According to the specification if one of the devices has a NoInputNoOutput capability, then the pairing mode used is named Just Works and such a link should be considered unauthenticated and vulnerable to MitM attacks. This results in an adjacent adversary being able to execute a practical attack and establish a MitM position.

Important distinction: In this case, the vehicle doesn't allow NoInputNoOutput devices to initiate a connection to the IVI, but fails to check the same for a connection initiated by the IVI. The attack window is smaller than in a usual NiNo attack but still exists.


Note on NiNo devices in the vehicular domain:
In the vehicular domain, the usage of NiNo devices such as headphones is not frequent if legal at all while driving. When it comes to the smartphone domain a connection to such devices is considered a feature and a usability trade-off to enable wireless headphones for example. As such a use-case is not present in the vehicular domain then it's better to disallow connection from such devices, which many of the manufacturers do already.


For the PoC steps please consult [contact extractor documentation](https://github.com/sgxgsx/BlueToolkit/wiki/Manual-Exploits)

#### Contact Extractor attack

The vehicle IVI system allows a physical adversary to extract previously shared through Bluetooth contacts. This happens due to incorrect handling of access control for newly created BT sessions for already known MAC addresses. 

Examples of vulnerable cars:
<img src="/static/exampleRenault.png" alt="ExampleRenault">
 
For the PoC steps please consult [contact extractor documentation](https://github.com/sgxgsx/BlueToolkit/wiki/Manual-Exploits)
