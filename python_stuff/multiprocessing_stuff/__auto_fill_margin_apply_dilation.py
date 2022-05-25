def __auto_fill_margin_apply_dilation( keys, values, image_size, image_channels, pixels, threshold, simple_queue=None ):
    if simple_queue is not None: simple_queue.put(1)

    for i in range(len(keys)):
        i2 = keys[i]
        value = values[i]

        if len(value) > 0:
            final_color = list(pixels[i2:i2 + image_channels])

            total_color = [0.0] * image_channels
            total_weight = 0.0

            for composite_data in value:
                weight = composite_data[0][-1]  # * composite_data[1]
                total_weight += weight
                for j in range(image_channels - 1):
                    total_color[j] = total_color[j] + (composite_data[0][j] * weight)

            new_color = []
            for j in range(image_channels - 1):
                new_color.append(total_color[j] / total_weight)

            new_alpha = 0.0
            for composite_data in value:
                aa = composite_data[0][-1] * composite_data[1]
                ab = new_alpha
                ao = aa + (ab * (1 - aa))
                new_alpha = ao
            new_color.append(new_alpha)

            # We composite this new color over the existing one.
            aa = new_color[-1]
            ab = final_color[-1]

            ao = aa + (ab * (1 - aa))
            for j in range(image_channels - 1):
                ca = new_color[j]
                cb = final_color[j]

                co = ((ca * aa) + ((cb * ab) * (1 - aa))) / ao

                final_color[j] = co
            final_color[-1] = ao

            if final_color[-1] >= threshold:
                final_color[:-1] = new_color[:-1]
                final_color[-1] = 1.0

            pixels[i2:i2 + image_channels] = final_color

    if simple_queue is not None:
        simple_queue.put(2)
        return 0