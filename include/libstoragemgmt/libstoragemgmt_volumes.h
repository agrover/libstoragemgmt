/*
 * Copyright (C) 2011 Red Hat, Inc.
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Author: tasleson
 *
 */

#ifndef LIBSTORAGEMGMT_VOLUMES_H
#define	LIBSTORAGEMGMT_VOLUMES_H

#ifdef	__cplusplus
extern "C" {
#endif

/**
 * Frees the memory for each of the volume records and then the array itself.
 * @param init  Array to free.
 * @param size  Size of array.
 */
void lsmVolumeRecordFreeArray( lsmVolumePtr init[], uint32_t size);

/**
 * Retrieves the volume id.
 * Note: returned value only valid when v is valid!
 * @param v     Volume ptr.
 * @return Volume id.
 */
const char* lsmVolumeIdGet(lsmVolumePtr v);

/**
 * Retrieves the volume name (human recognizable
 * Note: returned value only valid when v is valid!
 * @param v     Volume ptr.
 * @return Volume name
 */
const char* lsmVolumeNameGet(lsmVolumePtr v);

/**
 * Retrieves the SCSI page 83 unique ID.
 * Note: returned value only valid when v is valid!
 * @param v     Volume ptr.
 * @return SCSI page 83 unique ID.
 */
const char* lsmVolumeVpd83Get(lsmVolumePtr v);

/**
 * Retrieves the volume block size.
 * @param v     Volume ptr.
 * @return Volume block size.
 */
uint64_t lsmVolumeBlockSizeGet(lsmVolumePtr v);

/**
 * Retrieves the number of blocks.
 * @param v     Volume ptr.
 * @return      Number of blocks.
 */
uint64_t lsmVolumeNumberOfBlocks(lsmVolumePtr v);

/**
 * Retrieves the operational status of the volume.
 * @param v     Volume ptr.
 * @return Operational status of the volume, @see lsmVolumeOpStatus
 */
uint32_t lsmVolumeOpStatusGet(lsmVolumePtr v);

#ifdef	__cplusplus
}
#endif

#endif	/* LIBSTORAGEMGMT_INITIATORS_H */

