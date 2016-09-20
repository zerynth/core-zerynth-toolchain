import viper.viperconf as vconf
import viper.toolbelt as tb
import os.path
import os
import json

families = {}


def generate_families():
    global families
    families = {}

    #for pkg,v in tb.vpm.query_packages(by=("type","=","vhal"),installed=True,testing=tb.is_testing()):
    #    try:
    #        with open(os.path.join(vconf.envdirs["vhal"],pkg.path,"vhal.json"),"r") as ff:
    #            vh = json.load(ff)
    #            families.update(vh)
    #    except Exception as e:
    #        print(e)
    for root, dirs, files in os.walk(vconf.envdirs["vhal"]):
        if "vhal.json" in files:
            try:
                with open(os.path.join(root,"vhal.json"),"r") as ff:
                    vh = json.load(ff)
                    families.update(vh)
            except Exception as e:
                print(e)
    return families

def get_families():
    global families
    if not families:
        generate_families()
    return families


# families = {
#     "stm32f4":{
#         "path":"vm/common/vhal/ARMCMx/stm32f4",
#         "vhal":{
#             "VHAL_PWM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_PWM"]
#             },
#             "VHAL_ICU":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_ICU"]
#             },
#             "VHAL_HTM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_HTM"]
#             },
#             "VHAL_ADC":{
#                 "src":["vhal_adc.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_ADC","VHAL_DMA"]
#             },
#             "VHAL_SPI":{
#                 "src":["vhal_spi.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_SPI","VHAL_DMA"]
#             }
#         }
#     },
#     "stm32f2":{
#         "path":"vm/common/vhal/ARMCMx/stm32f2",
#         "vhal":{
#             "VHAL_PWM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_PWM"]
#             },
#             "VHAL_ICU":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_ICU"]
#             },
#             "VHAL_HTM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_HTM"]
#             },
#             "VHAL_ADC":{
#                 "src":["vhal_adc.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_ADC","VHAL_DMA"]
#             },
#             "VHAL_SPI":{
#                 "src":["vhal_spi.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_SPI","VHAL_DMA"]
#             },
#             "VHAL_SDIO":{
#                 "src":["vhal_sdio.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_SDIO","VHAL_DMA"]
#             }
#         }
#     },
#     "stm32f1":{
#         "path":"vm/common/vhal/ARMCMx/stm32f1",
#         "vhal":{
#             "VHAL_PWM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_PWM"]
#             },
#             "VHAL_ICU":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_ICU"]
#             },
#             "VHAL_HTM":{
#                 "src":["vhal_tim.c","../stm32common/stm32_timers.c"],
#                 "inc":[".","inc","../stm32common"],
#                 "defs":["VHAL_HTM"]
#             },
#             "VHAL_ADC":{
#                 "src":["vhal_adc.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_ADC","VHAL_DMA"]
#             },
#             "VHAL_SPI":{
#                 "src":["vhal_spi.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_SPI","VHAL_DMA"]
#             }
#         }
#     },
#     "atmelSAM3X":{
#         "path":"vm/common/vhal/ARMCMx/atmelSAM3X",
#         "vhal":{
#             "VHAL_PWM":{
#                 "src":["vhal_tim.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_PWM"]
#             },
#             "VHAL_ICU":{
#                 "src":["vhal_tim.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_ICU"]
#             },
#             "VHAL_HTM":{
#                 "src":["vhal_tim.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_HTM"]
#             },
#             "VHAL_ADC":{
#                 "src":["vhal_adc.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_ADC"]
#             },
#             "VHAL_SPI":{
#                 "src":["vhal_spi.c","vhal_dma.c"],
#                 "inc":[".","inc"],
#                 "defs":["VHAL_SPI","VHAL_DMA"]
#             }
#         }

#     }
# }