/*windows
*	/windows
*/
/*
* Copyright (c) 2017, Intel Corporation
*
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and associated documentation files (the "Software"),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
        elif args.tp == "check_diff_staged":
            check_diff_staged(args.gfx_driver)
            print("check_diff_staged")
        elif args.tp=="all":
            # run old code mode
            print("all")
        else:
            print("wrong")
    except:	whindows
        raise Exception("The search program didn't run correctly!")
    return 0

*/
//!
//! \file     codechal_setting_ext.h
//! \brief    Defines class CodechalSetting
//!
#ifndef __CODECHAL_SETTING_EXT_H__
#define __CODECHAL_SETTING_EXT_H__

#include "codechal_setting.h"

typedef struct _MHW_PAVP_ENCRYPTION_PARAMS *PMHW_PAVP_ENCRYPTION_PARAMS;

//!
//! \enum   CodechalDecodePkEncType
//! \brief  enum constant for decode encryption type on Windows porting kit
//!
enum CodechalDecodePkEncType
{
    CodechalDecodePkNone = 0x00,    //!< Clear mode decode
    CodechalDecodePk3Cenc,          //!< HEVC decode PR3.0 and Google AVC widevine on Windows
    CodechalDecodePk4Cenc,          //!< HEVC,AVC and VP9 CENC decode on PR4.0
    CodechalDecodePk4Cbcs,          //!< AVC CBCS decode on PR4.0
};

//!
//! \class  CodechalSettingExt 
//! \brief  Settings used to finalize the creation of the CodecHal device 
//!
/* windows
libva
DXVA
windows*/
class CodechalSettingExt: public CodechalSetting
{
public:
    // Cenc Decode for AVC decode on PR3.0.
    bool isCencInUse = false;           //!< Flag to indicate the PR3.0 DDI is in use (as opposed to Intel defined DDI for HuC-based DRM).

    // Secure decode encryption type on Windows PK3/4, for HEVC PR3/4, AVC Widevine, AVC PR4 on Windows.
    CodechalDecodePkEncType secureDecodePkEncType = CodechalDecodePkNone; //!< Flag to indicate the encryption type is in use (as opposed to Intel defined DDI for HuC-based DRM).

    bool isMmcEnabled = false;          //!< Flag to indicate if Mmc is enabled
	/windows
    //!
    //! \brief    Return the indicate if cenc advance is used or not 
    //!
    virtual bool CheckCencAdvance();
    //!
    //! \brief    Return the decode enc type 
    //!
    virtual uint32_t DecodeEncType();
 };
 add some new features and keywords
 DXVA-libva + windows
 // new windows 
gen11, gen12
gen12
//gen11 
/* gen12 */
#endifffffff thisaha
