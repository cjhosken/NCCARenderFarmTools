#!/usr/bin/env python
"""
 Licensed Materials - Property of Pipelinefx L.L.C.

 (C) COPYRIGHT Pipelinefx Limited Liability Corporation.
  All Rights Reserved.

  US Government Users Restricted Rights - Use, duplication or
  disclosure restricted by GSA ADP Schedule Contract with
  Pipelinefx L.L.C.

 $DateTime: 2020/10/14 03:27:11 $
 $Change: 22715 $

 Written by: Brian Knudson / PFX
             briank@pipelinefx.com
             2015-04-16

 Description:
  API access to central preferences (new in Qube 6.8)

"""

import re
import sys
import inspect
import logging
import collections
import traceback

try:
    import qb
except ImportError:
    for api_path in ("/Applications/pfx/qube/api/python/",
                     "/usr/local/pfx/qube/api/python/",
                     "C:\\Program Files\\pfx\\qube\\api\\python",
                     "C:\\Program Files (x86)\\pfx\\qube\\api\\python"):
        if api_path not in sys.path and os.path.exists(api_path):
            sys.path.insert(0,api_path)
            break
    import qb

VALID_ENTITY_TAILS = ("value",
                      "display",
                      "label",
                      "hide",
                      "mandate",
                      )


# entity: submission or submission.nuke_cmdline or submission.nuke_cmdline.name.name
#         ui or ui.search_field

def convertToDotNotation(d, key, dots, ignore_key=None):
    """
    Converts a nested dict into a one level dict with dotted notation for keys
    @param d: a [nested] dictionary
    @param key: the root of this nested dict
    @param dots: a list of dots leading up to the current position
    @returns: single level dict with keys that are the dotted notation representation
      of the original nested dict, i.e.

      >>> d = {'a':1,'b':{'sa':11,'sb':22,'sc':{'ssa':111,'ssb':222}},'c':3,}
      >>> convertToDotNotation(d,'',[])
      {'a': 1, 'b.sa': 11, 'b.sb': 22, 'b.sc.ssa': 111, 'b.sc.ssb': 222, 'c': 3}

    """
    if isinstance(d, dict):
        for k in d:
            convertToDotNotation(d[k], key + '.' + str(k) if key else k, dots, ignore_key)
    else:
        if ignore_key:
            if key.count(ignore_key) == 0:
                dots.append((key,d))
        else:
            dots.append((key,d))
    return dict(dots)


def getUsingDotNotation(d,dot_notation):
    """
    Given a dictinoary, d, use the dot_notation "path" to get to the
    dictionary entry.  i.e. dot_notation of "foo.bar.baz" will return
    d['foo']['bar']['baz'] or a KeyError if the path cannot be resolved.

    @param d: dictionary
    @param dot_notation: string
    @returns: dictionary value at the given location
    """
    exploded_dot_notation = dot_notation.split('.')
    invalid = "??INVALID??"

    if len(exploded_dot_notation) == 1:
        ret = d.get(exploded_dot_notation[0],invalid)
        if ret == invalid:
            raise KeyError("Invalid key '%s'" % exploded_dot_notation[0])
        return d[exploded_dot_notation[0]]

    if d.get(exploded_dot_notation[0],invalid) == invalid:
        raise KeyError("Invalid key2 '%s'" % exploded_dot_notation[0])
    return getUsingDotNotation(d[exploded_dot_notation[0]], '.'.join(exploded_dot_notation[1:]))


def setUsingDotNotation(d,dot_notation,v):
    """
    Given a dictinoary, d, use the dot_notation "path" to set to the
    dictionary entry.  i.e. dot_notation of "foo.bar.baz" will set
    d['foo']['bar']['baz'] = v.  If the path cannot be resolved,
    it will be created.

    @param d: dictionary
    @param dot_notation: string
    @param v: value to set
    @returns: dictionary value at the given location
    """
    exploded_dot_notation = dot_notation.split('.')

    if len(exploded_dot_notation) == 1:
        d[exploded_dot_notation[0]] = v
        return True

    d.setdefault(exploded_dot_notation[0],{})
    if not isinstance(d[exploded_dot_notation[0]],collections.Mapping):
        logging.debug("Replacing value for key '%s' in dictionary during setUsingDotNotation" % exploded_dot_notation[0])
        d[exploded_dot_notation[0]] = {}

    return setUsingDotNotation(d[exploded_dot_notation[0]], '.'.join(exploded_dot_notation[1:]),v)


def nestedUpdate(d,u):
    """
    Takes two dictionaries and updates values from the first with
    those of the second, and does so recursively.  This function also
    looks for "mandated" items.  If a "mandate" exists in d, then the u
    values are ignored.
    @param d: dictionary that needs updating
    @param u: dictionary with value to be used for updating d
    @returns: d updated with u's values.
    """
    for k,v in u.items():
        if isinstance(v,collections.Mapping):
            if d.get(k,{}).get("mandate"):
                logging.debug("nestedUpdate skipping %s because it was previously mandated" % k)
                continue
            r = nestedUpdate(d.get(k,{}),v)
            try:
                logging.debug("nestedUpdate recursive update d[%s] (%s) with %s" % (k,d[k],r))
            except KeyError:
                logging.debug("nestedUpdate recursive update d[%s] with %s" % (k,r))
            d[k] = r

        else:
            try:
                logging.debug("nestedUpdate updating d[%s] (%s) with %s" % (k,d[k],u[k]))
            except:
                logging.debug("nestedUpdate adding d[%s] with %s" % (k,v))
            d[k] = v
    return d


def __listToDict(l,key):
    """
    This function converts a list of dictionaries to a single dictionary by
    keying the resulted dict based on the given key retrieved from each
    dict in the list.

    @param l: the list of dicts
    @param key: the key from each dict in the list that will be used as
      the key in the returned list

    @returns: dict of dicts
    """
    ret = {}
    for i in l:
        ret[i.get(key,"UNKNOWN")] = i
    return ret


def __reduceDictList(l,key,val):
    """
    takes a list of one-level dict of many keys and returns a single dict with
    keys based on each d['key'] with the a value of d['val']

    @param l: a list of dictionaries
    @param key: the resulting dict will have keys of each d[n]['key']
    @param val: the resulting dict will have values based on each of d[n]['val']

    @returns: a dictionary
    """
    if not l:
        return {}
    return dict([(i.get(key,"??"),i.get(val,"??")) for i in l])


def __mandater(l,level):
    """
    Looks through the given list of dictionaries and adds a "mandate_level" key
    to any dict that has a mandate.  The value of "mandate_level" will be the
    given "level," i.e. common_allusers

    @param l: a list of dictionaries
    @param level: (string) the value for "mandate_level" if a mandate is found.
    """
    for d in l:
        if d.get("mandate"):
            d["mandate_level"] = level


def getPref(preference_type, entity_path, tier=None, preset=None, user=None,
        constrain=False, detailed=False, value_key="entity_value",
        accumulate_results=True):
    """
    Retrieve a set of preferences from the preference server.  Preferences are
    returned in dictionary format.

    @param preference_type: type of preference we are fetching, i.e. submission or UI
    @param entity_path: dotted notation of the thing for which we want preferences,
      i.e. nuke_cmdline or nuke_cmdline.parameters.nuke_version
    @param preset: the specific preset level in use, if one is in use (default: None)
    @param user: the username making the request
    @param constrain: if True, the return will be for only the tier/preset/user specified,
      otherwise the accumulated preferences up to the given tier/preset/user are returned.
      (default: False)
    @param detailed: if True, return all fields related to this param as the value of the
      return dict.  So, instead of getting {entity_path:entity_value}, you will get:
      {entity_path : {'entity_path':entity_path, 'entity_value':entity_value,
                      'mandate':True,'mandate_level':mandate_level,'username':someuser, 'etc':etc}}
      "mandate_level" will be one of [common|specific]_[base|preset|user|user_preset]
    @param value_key: if provided, use the given key to populate the value of the return.
      For example, the default is to use "entity_value" in which case you would get a return
      dict that looks like {entity_path:entity_value}.  You could, however, supply "id" as the
      value_key_override and you would get back {entity_path:id}.  Default: "entity_value"

    @returns: a aggregated dictionary of preference variable/values for the
      requested entity_path
    """

    common_prefs = []
    studio_prefs = []
    preset_prefs = []
    user_prefs = []

    entity_root = entity_path.split('.')[0]
    common_entity_path = entity_path.replace(entity_root,"common",1)

    #################
    # Fetch all prefs that match the entity_path from supervisor
    #################

    common_prefs_all = qb.getpreferences(preference_type, common_entity_path)

    if entity_path == '' or common_entity_path != entity_path:
        # get specific parameters that match our entity_root
        specific_prefs_all = qb.getpreferences(preference_type, entity_path)
    else:
        specific_prefs_all = []

    # ---------------------------------------
    #   sanitize the the data returned by the API call
    # ---------------------------------------
    try:
        for l in [common_prefs_all, specific_prefs_all]:
            for d in l:
                if d['preset_name'] == '0':
                    d['preset_name'] = None
                if d['username'] == '0':
                    d['username'] = None
    except TypeError as e:
        print(e)

    # if accumulate_results is False, then the user wants all data back,
    # including all data up the preference chain.  For example,
    # if priority is set at both the common and the specific tier for a UI,
    # then only the specific tier data will be returned when accumulate_results
    # is True. If accumulate_results is False, however, then both the common
    # and specific preferences will be returned (useful for seeing all data in
    # the db without direct queries)
    if not accumulate_results:
        if tier == "common":
            prefs_all = common_prefs_all
        elif tier == "specific":
            if common_entity_path == entity_path:
                prefs_all = common_prefs_all
            else:
                prefs_all = specific_prefs_all
        else:
            prefs_all = common_prefs_all + specific_prefs_all
        filtered_prefs = [pref for pref in prefs_all if
                          pref.get("tier") == tier and
                          pref.get("preset_name") == preset and
                          pref.get("username") == user]
        if detailed: return __listToDict(filtered_prefs,"entity_path")
        return __reduceDictList(filtered_prefs,"entity_path",value_key)


    #################
    #
    # Setup "storage"
    #
    #################

    common_base = {}          # will hold all common prefs that don't belong to a user or a preset
    common_preset = {}        # will hold all common prefs that don't belong to a user, but are part of a preset
    common_user = {}          # will hold all common prefs that belong to a user, but are not part of a preset
    common_user_preset = {}   # will hold all common prefs that belong to a user, and are part of a preset

    specific_base = {}        # will hold all specific prefs that don't belong to a user or a preset
    specific_preset = {}      # will hold all specific prefs that don't belong to a user, but are part of a preset
    specific_user = {}        # will hold all specific prefs that belong to a user, but are not part of a preset
    specific_user_preset = {} # will hold all specific prefs that belong to a user, and are part of a preset

    limit_reached = False # Flag to stop accumulating data
 
    #stopped here, 2015-06-02: Need to add a new "limit" paramter (or something like that) that
    # will allow the prefs to accumulate up to the requested tier/preset/user.  This is what
    # will be used by the prefs.
    # Also need to add the level at which each pref is set, and return that with the detailed
    # info.  This will allow the UI to determine which things to decorate/color during edit

    #################
    #
    # Common prefs
    #
    #################

    common_base = [pref for pref in common_prefs_all if
                   pref.get("preset_name") is None and
                   pref.get("username") is None]
    __mandater(common_base,"common_base")
    if not limit_reached and tier == "common" and preset is None and user is None:
        limit_reached = True
        if constrain:
            # if we're constraining output, asked for common tier, but gave no preset or user, then:
            if detailed: return __listToDict(common_base,"entity_path")
            return __reduceDictList(common_base,"entity_path",value_key)
    
    # convert common_base so that it's a dict keyed on the path (so we can do a nested update)
    common_base = __listToDict(common_base,"entity_path")
    
    if not limit_reached and preset is not None:
        common_preset = [pref for pref in common_prefs_all if
                         pref.get("preset_name") == preset and
                         pref.get("username") is None]
        __mandater(common_preset,"common_preset")
        if tier == "common" and user is None:
            limit_reached = True
            if constrain:
                # if we're constraining output, asked for common tier and some preset but no user, then:
                if detailed: return __listToDict(common_preset,"entity_path")
                return __reduceDictList(common_preset,"entity_path",value_key)
        
        # convert common_preset so that it's a dict keyed on the path (so we can do a nested update)
        common_preset = __listToDict(common_preset,"entity_path")
        
    if not limit_reached and user is not None:
        common_user = [pref for pref in common_prefs_all if
                       pref.get("preset_name") is None and
                       pref.get("username") == user]
        __mandater(common_user,"common_user")
        if tier == "common" and preset is None:
            limit_reached = True
            if constrain:
                # if we're constraining output, asked for common tier and some user but no preset, then:
                if detailed: return __listToDict(common_user,"entity_path")
                return __reduceDictList(common_user,"entity_path",value_key)

        # convert common_user so that it's a dict keyed on the path (so we can do a nested update)
        common_user = __listToDict(common_user,"entity_path")
        
        if not limit_reached and preset is not None:
            common_user_preset = [pref for pref in common_prefs_all if
                                  pref.get("preset_name") == preset and
                                  pref.get("username") == user]
            __mandater(common_user_preset,"common_user_preset")
            if tier == "common":
                limit_reached = True
                if constrain:
                    # if we're constraining output, asked for common and made it this far, then preset and user are defined
                    if detailed: return __listToDict(common_user_preset,"entity_path")
                    return __reduceDictList(common_user_preset,"entity_path",value_key)

            # convert common_user_preset so that it's a dict keyed on the path (so we can do a nested update)
            common_user_preset = __listToDict(common_user_preset,"entity_path")

    # Combine common prefs...

    # combine base and preset:
    common_prefs = nestedUpdate(common_base,common_preset)

    # combine base/preset and user:
    common_prefs = nestedUpdate(common_prefs,common_user)

    # combine base/preset/user and user_preset:
    common_prefs = nestedUpdate(common_prefs,common_user_preset)

    #################
    #
    # Specific prefs
    #
    #################

    if not limit_reached:
        specific_base = [pref for pref in specific_prefs_all if
                         pref.get("preset_name") is None and
                         pref.get("username") is None]
        __mandater(specific_base,"specific_base")
        if tier == "specific" and preset is None and user is None:
            limit_reached = True
            if constrain:
                # if we're constraining output, asked for specific tier, but gave no preset or user, then:
                if detailed: return __listToDict(specific_base,"entity_path")
                return __reduceDictList(specific_base,"entity_path",value_key)

        # convert specific_base so that it's a dict keyed on the path (so we can do a nested update)
        specific_base = __listToDict(specific_base,"entity_path")

    if not limit_reached and preset is not None:
        specific_preset = [pref for pref in specific_prefs_all if
                           pref.get("preset_name") == preset and
                           pref.get("username") is None]
        __mandater(specific_preset,"specific_preset")
        if tier == "specific" and user is None:
            limit_reached = True
            if constrain:
                # if we're constraining output, asked for specific tier and some preset but no user, then:
                if detailed: return __listToDict(specific_preset,"entity_path")
                return __reduceDictList(specific_preset,"entity_path",value_key)

        # convert specific_preset so that it's a dict keyed on the path (so we can do a nested update)
        specific_preset = __listToDict(specific_preset,"entity_path")

    if not limit_reached and user is not None:
        specific_user = [pref for pref in specific_prefs_all if
                         pref.get("preset_name") is None and
                         pref.get("username") == user]
        __mandater(specific_user,"specific_user")
        if tier == "specific" and preset is None:
            limit_reached = True
            if constrain:
                # if we're constraining output, asked for specific tier and some user but no preset, then:
                if detailed: return __listToDict(specific_user,"entity_path")
                return __reduceDictList(specific_user,"entity_path",value_key)

        # convert specific_user so that it's a dict keyed on the path (so we can do a nested update)
        specific_user = __listToDict(specific_user,"entity_path")
        
        if not limit_reached and preset is not None:
            specific_user_preset = [pref for pref in specific_prefs_all if
                                    pref.get("preset_name") == preset and
                                    pref.get("username") == user]
            __mandater(specific_user_preset,"specific_user_preset")
            if tier == "specific":
                limit_reached = True
                if constrain:
                    # if we're constraining output, asked for specific and made it this far, then preset and user are defined
                    if detailed: return __listToDict(specific_user_preset,"entity_path")
                    return __reduceDictList(specific_user_preset,"entity_path",value_key)

            # convert specific_user_preset so that it's a dict keyed on the path (so we can do a nested update)
            specific_user_preset = __listToDict(specific_user_preset,"entity_path")

    # Combine specific prefs...

    # combine base and preset:
    specific_prefs = nestedUpdate(specific_base,specific_preset)

    # combine base/preset and user:
    specific_prefs = nestedUpdate(specific_prefs,specific_user)

    # combine base/preset/user and user_preset:
    specific_prefs = nestedUpdate(specific_prefs,specific_user_preset)

    ################################
    #
    # Combine common and specific
    #
    ################################

    # convert common to specific so we can do one last nested update:
    common_pattern = re.compile('^common')
    for k,v in common_prefs.copy().items():
        key = re.sub(common_pattern,entity_root,k)
        v['entity_path'] = key
        common_prefs[key] = v
        del(common_prefs[k])

    combined_prefs = nestedUpdate(common_prefs,specific_prefs)

    if detailed:
        return combined_prefs
    
    # one liner:
    # - pulls the values from the result (which is a list of dicts)
    # - reduces the list of dict into a single dict
    # returns that
    return __reduceDictList(list(combined_prefs.values()),"entity_path",value_key)


def getPreferenceUsers(preference_type):
    """
    Retrieve a list of users who have preferences

    @param preference_type: type of preference we are fetching, i.e. submission or UI

    @returns: a list of strings (usernames)
    """
    prefs_users = set([x['username'] for x in qb.getpreferences(preference_type, '') if x['username'] != '0'])
    return list(prefs_users)


def setPref(preference_type, entity_path, entity_value, tier="specific", preset=None, user=None, mandate=False, dry=False):
    """
    Given an entity_path, update the database at the given tier (studio_common,
    studio_specific, preset_specific, user_specifc) with the given data.

    @param preference_type: type of prefernce we are fetching, i.e. submission or UI
    @param entity_path: The entity we'll be updating.  This can be a single value
      or a an entire submission UI
    @param tier: The preference tier at which these values will be stored.
      Possible options: common, specific
    @param data: The data to be stored.  data can be a single value or a dictionary
    @param preset: The preset name if one is in use
    @param user: The username, if setting for a specific user
    @param dry: Only do a dry-run, don't actually set the pref in the DB

    @returns: a confirmation of the thing that was set.
    """
    pref_stored = False
    # ---------------------------------------
    #   can be passed QStrings from AV and other PyQT apps
    # ---------------------------------------
    tier = str(tier)
    if user is not None:
        user = str(user)

    if preference_type == "submission":
        tail = entity_path.split('.')[-1]
        if tail not in VALID_ENTITY_TAILS:
            logging.error("Trying to set an entity with unknown tail. Bailing out. %s" % entity_path)
            return

    if dry:
        cf = inspect.currentframe()
        frame_args = inspect.getargvalues(cf)[0]
        del cf
        print("(dry-run):")
        print(['%s: %s' % (x, locals().get(x, 'NOT FOUND')) for x in frame_args].__repr__())
        pref_stored = True
    else:
        try:
            ret_val = qb.setpreference(preference_type, entity_path, entity_value, tier, preset, user, mandate)
        except Exception as e:
            logging.warning('Failed to set preference')
            print(traceback.format_exc())
            ret_val = False

        if ret_val is True:
            pref = getPref(preference_type=preference_type, entity_path=entity_path, preset=preset, user=user, constrain=True)
            pref_stored = True

            for k,v in pref.items():
                if pref[k] != entity_value:
                    logging.warning('Preference not properly stored')
                    pref_stored = False

    return pref_stored


def deletePref(preference_type, entity_path, tier="specific", preset=None, user=None, dry=False):
    """
    delete a preference at a given level.

    @param preference_type: type of prefernce we are deleting, i.e. submission or UI
    @param entity_path: The entity we'll be deleting.  This *must* be a single,
      matching path, i.e. submission.nuke_cmdline.parameters.priority.fields.priority.value
    @param tier: The preference tier at which these values will be stored.
      Possible options: common, specific
    @param preset: The preset name of the preference to be deleted. None is acceptable.
    @param user: The username of the preference owner if one exists
    """
    pref_deleted = False

    tier = str(tier)
    if user is None:
        user = ''
    else:
        user = str(user)

    try:
        pref_deleted = qb.deletepreference(preference_type, entity_path, tier, preset, user)
    except Exception as e:
        logging.warning('Failed to delete preference')
        print(traceback.format_exc())

    return pref_deleted
