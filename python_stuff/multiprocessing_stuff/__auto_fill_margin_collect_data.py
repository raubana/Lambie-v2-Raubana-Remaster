def __auto_fill_margin_collect_data( edge_pixels, image_size, image_channels, pixels, kernel, simple_queue=None ):
    if simple_queue is not None: simple_queue.put(1)

    output = {}

    for i in edge_pixels:
        our_pixel = pixels[i:i + image_channels]

        if our_pixel[-1] > 0.0:
            will_dilate = False

            #x, y = index_to_coords(i, image_size, image_channels)
            i2 = int(i / image_channels)
            x = int(i2 % image_size[0])
            y = int(i2 / image_size[0])

            for offset_data in kernel:
                new_coords = (x + offset_data[0][0], y + offset_data[0][1])

                if new_coords[0] >= 0 and new_coords[1] >= 0 and new_coords[0] < image_size[0] and new_coords[1] < image_size[1]:
                    i3 = (new_coords[0] * image_channels) + (new_coords[1] * image_size[0] * image_channels) #coords_to_index(new_coords, image_size, image_channels)
                    offset_pixel = pixels[i3:i3 + image_channels]

                    if our_pixel[-1] > 0.0 and offset_pixel[-1] < 1.0 and our_pixel[-1] > offset_pixel[-1]:
                        if i3 not in output: output[i3] = []
                        output[i3].append( (our_pixel, offset_data[1]) )

                        will_dilate = True

            if will_dilate:
                if i not in output: output[i] = []

    if simple_queue is not None:
        simple_queue.put(output)
        if simple_queue is not None: simple_queue.put(2)
        return 0
    else:
        return output