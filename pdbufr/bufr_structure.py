import collections
import typing as T

import attr
import eccodes  # type: ignore

from . import bufr_filters


@attr.attrs(auto_attribs=True, frozen=True)
class BufrKey:
    level: int
    rank: int
    name: str

    @classmethod
    def from_level_key(cls, level: int, key: str) -> "BufrKey":
        rank_text, sep, name = key.rpartition("#")
        if sep == "#":
            rank = int(rank_text[1:])
        else:
            rank = 0
        return cls(level, rank, name)

    @property
    def key(self) -> str:
        if self.rank:
            prefix = f"#{self.rank}#"
        else:
            prefix = ""
        return prefix + self.name


IS_KEY_COORD = {"subsetNumber": True, "operator": False}


def message_structure(message: T.Mapping[str, T.Any],) -> T.Iterator[T.Tuple[int, str]]:
    level = 0
    coords: T.Dict[str, int] = collections.OrderedDict()
    for key in message:
        name = key.rpartition("#")[2]

        if name in IS_KEY_COORD:
            is_coord = IS_KEY_COORD[name]
        else:
            try:
                code = message[key + "->code"]
                is_coord = int(code[:3]) < 10
            except (KeyError, eccodes.KeyValueNotFoundError):
                is_coord = False

        while is_coord and name in coords:
            _, level = coords.popitem()  # OrderedDict.popitem uses LIFO order

        yield (level, key)

        if is_coord:
            coords[name] = level
            level += 1


def filtered_keys(
    message: T.Mapping[str, T.Any], include: T.Tuple[str, ...] = (),
) -> T.Iterator[BufrKey]:
    for level, key in message_structure(message):
        bufr_key = BufrKey.from_level_key(level, key)
        if include == () or bufr_key.name in include or bufr_key.key in include:
            yield bufr_key


def make_message_uid(message: T.Mapping[str, T.Any]) -> T.Tuple[T.Optional[int], ...]:
    message_uid: T.Tuple[T.Optional[int], ...]

    message_uid = (
        message["edition"],
        message["masterTableNumber"],
        message["numberOfSubsets"],
    )

    descriptors: T.Union[int, T.List[int]] = message["unexpandedDescriptors"]
    if isinstance(descriptors, int):
        message_uid += (descriptors, None)
    else:
        message_uid += tuple(descriptors) + (None,)

    try:
        delayed_descriptors = message["delayedDescriptorReplicationFactor"]
    except (KeyError, eccodes.KeyValueNotFoundError):
        delayed_descriptors = []

    if isinstance(delayed_descriptors, int):
        message_uid += (delayed_descriptors,)
    else:
        message_uid += tuple(delayed_descriptors)

    return message_uid


def cached_filtered_keys(
    message: T.Mapping[str, T.Any],
    cache: T.Dict[T.Tuple[T.Hashable, ...], T.List[BufrKey]],
    include: T.Iterable[str] = (),
) -> T.List[BufrKey]:
    message_uid = make_message_uid(message)
    include_uid = tuple(sorted(include))
    filtered_message_uid: T.Tuple[T.Hashable, ...] = message_uid + include_uid
    if filtered_message_uid not in cache:
        cache[filtered_message_uid] = list(filtered_keys(message, include_uid))
    return cache[filtered_message_uid]


def extract_observations(
    message: T.Mapping[str, T.Any],
    filtered_keys: T.List[BufrKey],
    filters: T.Dict[str, bufr_filters.BufrFilter] = {},
    base_observation: T.Dict[str, T.Any] = {},
) -> T.Iterator[T.Dict[str, T.Any]]:
    current_observation: T.Dict[str, T.Any]
    current_observation = collections.OrderedDict(base_observation)
    current_levels: T.List[int] = [0]
    failed_match_level: T.Optional[int] = None

    for bufr_key in filtered_keys:
        level = bufr_key.level
        name = bufr_key.name

        if failed_match_level is not None and level > failed_match_level:
            continue

        # TODO: make into a function
        if all(name in current_observation for name in filters) and (
            level < current_levels[-1]
            or (level == current_levels[-1] and name in current_observation)
        ):
            # copy the content of current_items
            yield dict(current_observation)

        while len(current_observation) and (
            level < current_levels[-1]
            or (level == current_levels[-1] and name in current_observation)
        ):
            current_observation.popitem()  # OrderedDict.popitem uses LIFO order
            current_levels.pop()

        value = message[bufr_key.key]
        if isinstance(value, float) and value == eccodes.CODES_MISSING_DOUBLE:
            value = None

        if name in filters:
            if filters[name].match(value):
                failed_match_level = None
            else:
                failed_match_level = level
                continue

        current_observation[name] = value
        current_levels.append(level)

    # yield the last observation
    if all(name in current_observation for name in filters):
        yield dict(current_observation)
