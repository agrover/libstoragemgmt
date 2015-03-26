# Copyright (C) 2015 Red Hat, Inc.,  Tony Asleson <tasleson@redhat.com>
# Distributed under the GNU General Public License, version 2.0.
# See: https://www.gnu.org/licenses/gpl-2.0.html
#
# Bash completion for lsmcli. This may be far from ideal, 
# suggestions & improvements appreciated!

potential_args=''


function join { local IFS="$1"; shift; echo "$*"; }

# Linear search of an array of strings for the specified string
listcontains() {
    declare -a the_list=("${!1}")

    for word in "${the_list[@]}" ; do
        [[ $word == $2 ]] && return 0
    done
    return 1
}

# Given a list of what is possible and what is on the command line return
# what is left.
# $1 What is possible
# Retults are returned in global string $potential_args
possible_args()
{
    local l=()

    for i in $1
    do
        listcontains COMP_WORDS[@] "$i"
        if [[ $? -eq 1 ]] ; then     
            l+=("$i")
        fi
    done

    potential_args=$( join ' ', "${l[@]}" )
}


_lsm() 
{
    local cur prev opts
    sep='#'
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts_short="-b -v -u -P -H -t -e -f -w -b"
    opts_long=" --help --version --uri --prompt --human --terse --enum \
              --force --wait --header --script "
    opts_cmds="list job-status capabilities plugin-info volume-create \
                volume-delete, volume-resize volume-replicate \
                volume-replicate-range volume-replicate-range-block-size \
                volume-dependants volume-dependants-rm volume-access-group \
                volume-mask volume-unmask access-group-create \
                access-group-delete access-group-add access-group-remove \
                volume-enable volume-disable"

    list_args="--type"
    list_type_args="volumes pools fs snapshots exports nfs_client_auth \
                    access_groups systems disks plugins target_ports"

    opts_filter="--sys --pool --vol --disk --ag --fs --nfs"

    cap_args="--sys"
    volume_create_args="--name --size --pool"
    volume_delete_args="--vol --force"  # Should force be here, to easy to tab through?"
    volume_resize_args="--vol --size --force" # Should force be here, to easy to tab through?"

    volume_replicate_args="--vol --name --rep-type"
    # Hmmm, this looks like a bug with CLI, should support lower and upper case?
    volume_rep_types="CLONE COPY MIRROR_ASYNC MIRROR_SYNC"

    volume_replicate_range_args="--src-vol --dst-vol --rep-type --src-start \
                                --dst-start --count --force" # Force ?

    volume_replication_range_bs="--sys"
    volume_dependants="--vol"

    volume_access_group_args="--vol"
    volume_masking_args="--vol --ag"

    access_group_create_args="--name --init --sys"
    access_group_delete_args="--ag"

    access_group_add_remove_args="--ag --init"

    volume_enable_disable_args="--vol"

    # Check if we have somthing present that we can help the user with
    case "${prev}" in
        --sys)
            # Is there a better way todo this?
            local items=`lsmcli list --type systems -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --pool)
            # Is there a better way todo this?
            local items=`lsmcli list --type pools -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --vol|--src-vol|--dst-vol)
            # Is there a better way todo this?
            local items=`lsmcli list --type volumes -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --disk)
            # Is there a better way todo this?
            local items=`lsmcli list --type disks -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --ag)
            # Is there a better way todo this?
            local items=`lsmcli list --type access_groups -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --init)
            # It would be better if we filtered the result with the access group
            # if it's present on the command line already.
            local items=`lsmcli list --type access_groups -t${sep} | awk -F "${sep}" '{print $3}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --nfs-export)
            # Is there a better way todo this?
            local items=`lsmcli list --type exports  -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        --tgt)
            # Is there a better way todo this?
            local items=`lsmcli list --type target_ports  -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;         
        --fs)
            local items=`lsmcli list --type fs -t${sep} | awk -F ${sep} '{print $1}'`
            COMPREPLY=( $(compgen -W "${items}" -- ${cur}) )
            return 0
            ;;
        snapshots)
            # Specific listing case where you need a fs too            
            if [[ ${COMP_WORDS[COMP_CWORD-2]} == '--type' && \
                  ${COMP_WORDS[COMP_CWORD-3]} == 'list' ]] ; then
                COMPREPLY=( $(compgen -W "--fs" -- ${cur}) )
                return 0
            fi
            ;;
        --type)
            COMPREPLY=( $(compgen -W "${list_type_args}" -- ${cur}) )
            return 0
            ;;
        --size|--count|--src-start|--dst-start|--name)
            # These we cannot lookup, so don't offer any values
            COMPREPLY=( $(compgen -W "" -- ${cur}) )
            return 0
            ;;
        --rep-type)
            COMPREPLY=( $(compgen -W "${volume_rep_types}" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

    case "${COMP_WORDS[1]}" in
        job-status)
            possible_args "--job"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        list)
            possible_args ${list_args}
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-create)
            possible_args "${volume_create_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-delete)
            possible_args "${volume_delete_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-resize)
            possible_args "${volume_resize_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-replicate)
            possible_args "${volume_replicate_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-replicate-range)
            possible_args "${volume_replicate_range_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-replicate-range-block-size)
            possible_args "${volume_replication_range_bs}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-dependants|volume-dependants-rm)
            possible_args "${volume_dependants}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-access-group)
            possible_args "${volume_access_group_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-mask|volume-unmask)
            possible_args "${volume_masking_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        access-group-create)
            possible_args "${access_group_create_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        access-group-delete)
            possible_args "${access_group_delete_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        access-group-add|access-group-remove)
            possible_args "${access_group_add_remove_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        volume-enable|volume-disable)
            possible_args "${volume_enable_disable_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        capabilities)
            possible_args "${cap_args}"
            COMPREPLY=( $(compgen -W "${potential_args}" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

    # Handle the case where we are starting out with nothing
    if [[ ${prev} == 'lsmcli' ]] ; then
        if [[ ${cur} == --* ]] ; then
            COMPREPLY=( $(compgen -W "${opts_long}"  -- ${cur}) )
            return 0
        fi

        if [[ ${cur} == -* ]] ; then
            COMPREPLY=( $(compgen -W "${opts_short}${opts_long}"  -- ${cur}) )
            return 0
        fi

        if [[ ${cur} == * ]] ; then
            COMPREPLY=( $(compgen -W "${opts_short}${opts_long}${opts_cmds}"  -- ${cur}) )
            return 0
        fi        
    fi
}
complete -F _lsm lsmcli
