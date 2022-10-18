#!/usr/bin/env python3
# -*- coding: utf-8 vi:noet
# SPDX-FileCopyrightText: 2016-2022 Jérôme Carretero <cJ@zougloub.eu> & contributors
# SPDX-License-Identifier: MIT

import logging

from pyueye import ueye


logger = logging.getLogger()


def check_res(h_cam, res):
	if res != ueye.IS_SUCCESS:
		s = ""
		for k, v in ueye.__dict__.items():
			if k.startswith("IS_") and v == res:
				s += "/" + k

		captureStatusInfo = ueye.UEYE_CAPTURE_STATUS_INFO()
		res2 = ueye.is_CaptureStatus(h_cam, ueye.IS_CAPTURE_STATUS_INFO_CMD_GET, captureStatusInfo, ueye.sizeof(captureStatusInfo))

		if res2 == ueye.IS_SUCCESS:
			nTotalInfos = captureStatusInfo.dwCapStatusCnt_Total
			logger.info("total=%s", nTotalInfos)
			logger.info(captureStatusInfo)
			for k, v in ueye.__dict__.items():
				if k.startswith("IS_CAP_STATUS"):
					x = captureStatusInfo.adwCapStatusCnt_Detail[v]
					if x != 0:
						logger.info("- %s: %s", k, x)

		else:
			logger.info("Res2: %s", res2)

		raise RuntimeError(f"Sez {res} ({s})")


class Camera:
	def __init__(self):
		...

	def check_res(self, res):
		h_cam = self._h_cam
		check_res(h_cam, res)

